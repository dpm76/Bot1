'''
Created on 26 nov. 2018

@author: david
'''
import logging
import math
import time

from sensor.pycomms.hmc5883l import HMC5883L
from sensor.pycomms.mpu6050 import MPU6050

PHYSICAL_MPU_AXES = ["pitch", "roll", "yaw"]
PHYSICAL_MPU_SIGNS = [1, -1, 1]
PHYSICAL_MAGNET_AXES = ["x", "y", "z"]
PHYSICAL_MPU_SIGNS = [-1, 1, -1]

MAGNET_CALIB_PERIOD = 0.02
MAGNET_CALIB_LPF_ALPHA = 0.1

logging.basicConfig(level=logging.DEBUG)

def readMagHeadings(mag, mpu):
    
    # get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize()
    
    # Get INT_STATUS byte
    mpuIntStatus = mpu.getIntStatus()
  
    if mpuIntStatus >= 2: # check for DMP data ready interrupt (this should happen frequently) 
        # get current FIFO count
        fifoCount = mpu.getFIFOCount()
        
        # check for overflow (this should never happen unless our code is too inefficient)
        if fifoCount == 1024:
            # reset so we can continue cleanly
            mpu.resetFIFO()
            logging.warn('FIFO overflow!')
            
            
        # wait for correct available data length, should be a VERY short wait
        fifoCount = mpu.getFIFOCount()
        while fifoCount < packetSize:
            fifoCount = mpu.getFIFOCount()
        
        # track FIFO count here in case there is > 1 packet available
        # (this lets us immediately read more without waiting for an interrupt)        
        fifoCount -= packetSize
        
        result = mpu.getFIFOBytes(packetSize)
        q = mpu.dmpGetQuaternion(result)
        g = mpu.dmpGetGravity(q)        
        ypr = mpu.dmpGetYawPitchRoll(q, g)
        
        angles = [
            PHYSICAL_MPU_SIGNS[0]*ypr[PHYSICAL_MPU_AXES[0]], 
            PHYSICAL_MPU_SIGNS[1]*ypr[PHYSICAL_MPU_AXES[1]],
            PHYSICAL_MPU_SIGNS[2]*ypr[PHYSICAL_MPU_AXES[2]]
        ]
            
        magDict = mag.getHeading()
        magField = [
            PHYSICAL_MPU_SIGNS[0]*magDict[PHYSICAL_MAGNET_AXES[0]],
            PHYSICAL_MPU_SIGNS[1]*magDict[PHYSICAL_MAGNET_AXES[1]],
            PHYSICAL_MPU_SIGNS[2]*magDict[PHYSICAL_MAGNET_AXES[2]],
        ]
        
        cosX = math.cos(angles[0])
        sinX = math.sin(angles[0])
        cosY = math.cos(angles[1])
        sinY = math.sin(angles[1])
        
        headX = magField[0] * cosY + magField[1] * sinX * sinY + magField[2] * cosX * sinY
        headY = magField[1] * cosX - magField[2] * sinX

        return (headX, headY)


def calibrate(mag, mpu, calibTime=30):

    headX, headY = readMagHeadings(mag, mpu)
    lastHeadX = maxHeadX = minHeadX = headX
    lastHeadY = maxHeadY = minHeadY = headY
    
    t0 = time.time()
    
    lpfComp = 1.0 - MAGNET_CALIB_LPF_ALPHA
    
    while time.time() - t0 < calibTime:
    
        headX, headY = readMagHeadings(mag, mpu)
                
        filtHeadX = lpfComp * lastHeadX + MAGNET_CALIB_LPF_ALPHA * headX
        filtHeadY = lpfComp * lastHeadY + MAGNET_CALIB_LPF_ALPHA * headY
        
        lastHeadX = filtHeadX
        lastHeadY = filtHeadY
        
        if filtHeadX > maxHeadX:
            maxHeadX = filtHeadX
            
        if filtHeadY > maxHeadY:
            maxHeadY = filtHeadY
        
        if filtHeadX < minHeadX:
            minHeadX = filtHeadX
            
        if filtHeadY < minHeadY:
            minHeadY = filtHeadY
            
        time.sleep(MAGNET_CALIB_PERIOD)

    offsetX = (minHeadX+maxHeadX)/2.0
    maxValX = maxHeadX - offsetX
    
    offsetY = (minHeadY+maxHeadY)/2.0
    maxValY = maxHeadY - offsetY
    
    return {"x": {"offset": offsetX, "max": maxValX}, "y":{"offset": offsetY, "max": maxValY}}


# MPU initialization
mpu = MPU6050(channel=1)
mpu.dmpInitialize()
mpu.setDMPEnabled(True)

# Magnetometer initialization
mag = HMC5883L(channel=1)
mag.initialize()

print("Press CTRL+C to finish")

try:
    
    calibTime = 30
    logging.info("Starting magnetometer calibration: move device for {0}s".format(calibTime))
    calib = calibrate(mag, mpu, calibTime)
    logging.info("Magnetometer calibration finished")
    
    while True:
        
        headX, headY = readMagHeadings(mag, mpu)
        
        normHeadX = (headX - calib["x"]["offset"])/calib["x"]["max"]
        normHeadY = (headY - calib["y"]["offset"])/calib["y"]["max"]
        
        heading = math.degrees(math.atan2(normHeadX, normHeadY))
        logging.info("Heading = {0:.3f}°".format(heading))
        time.sleep(0.1)

except KeyboardInterrupt:
    
    print("CTRL+C pressed. Finishing...")

finally:

    mpu.setDMPEnabled(False)
    mpu.setSleepEnabled(True)
    mag.setMode(HMC5883L.HMC5883L_MODE_IDLE)
    print("Bye!")

