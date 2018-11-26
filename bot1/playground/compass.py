'''
Created on 26 nov. 2018

@author: david
'''
import logging
import math
import time

from sensor.pycomms.hmc5883l import HMC5883L
from sensor.pycomms.mpu6050 import MPU6050


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
        
        angles = [ypr['pitch'], -ypr['roll'], ypr['yaw']]
            
        magDict = mag.getHeading()                
        
        headX = magDict["x"]*math.cos(angles[1])+magDict["y"]*math.sin(angles[0])*math.sin(angles[1])+magDict["z"]*math.cos(angles[0])*math.sin(angles[1])
        headY = magDict["y"]*math.cos(angles[0])-magDict["z"]*math.sin(angles[0])

        return (headX, headY)



def calibrate(mag, mpu, calibTime=30):

    headX, headY = readMagHeadings(mag, mpu)
    lastHeadX = maxHeadX = minHeadX = headX
    lastHeadY = maxHeadY = minHeadY = headY
    
    t0 = time.time()
    
    while time.time() - t0 < calibTime:
    
        headX, headY = readMagHeadings(mag, mpu)
                
        filtHeadX = 0.9*lastHeadX+0.1*headX
        filtHeadY = 0.9*lastHeadY+0.1*headY
        
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
            
        time.sleep(0.02)

    offsetX = (minHeadX+maxHeadX)/2.0
    maxValX = maxHeadX - offsetX
    
    offsetY = (minHeadY+maxHeadY)/2.0
    maxValY = maxHeadY - offsetY
    
    return {"x": {"offset": offsetX, "max": maxValX}, "y":{"offset": offsetY, "min": maxValY}}


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

