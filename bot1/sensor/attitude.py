'''
Created on 28 nov. 2018

@author: david
'''
import math
import time

from sensor.pycomms.hmc5883l import HMC5883L
from sensor.pycomms.mpu6050 import MPU6050


class AttitudeSensor(object):
    '''
    Provides angle tilt and acceleration vectors.
    In the background, it uses a inertial measurement unit (IMU), aka. motion process unit (MPU),
    and a magnetometer to provide data. 
    '''
    
    #TODO: 20181128 DPM: Get physical values from configuration
    PHYSICAL_MPU_AXES = ["pitch", "roll", "yaw"]
    PHYSICAL_MPU_SIGNS = [1, -1, 1]
    PHYSICAL_MAGNET_AXES = ["x", "y", "z"]
    PHYSICAL_MPU_SIGNS = [-1, 1, -1]
    MAX_HEADING_DIFF = math.radians(5.0)
    
    MAGNET_CALIB_PERIOD = 0.02
    MAGNET_CALIB_LPF_ALPHA = 0.1
    
    _2PI = 2.0*math.pi

    def __init__(self, channel=1):
        '''
        Constructor
        
        @param channel: I2C channel
        '''
        
        self._imu = MPU6050(channel=channel)
        self._mag = HMC5883L(channel=channel)
        
        self._imuPacketSize = 0
        self._magCalib = None
        self._imuAngleZOffset = 0.0
    
    
    def readAngles(self):
        
        raise NotImplementedError()
    
    
    def readAccels(self):
        
        raise NotImplementedError()
    
    
    def readAngleZ(self):
        
        headX, headY, angles = self._readSensors()
        normHeadX, normHeadY = self._normalizeHeadingComponents(headX, headY)
        
        magHead = math.atan2(normHeadX, normHeadY)
        imuHead = angles[2]
        
        if (magHead - imuHead)%AttitudeSensor._2PI < AttitudeSensor.MAX_HEADING_DIFF\
            and (imuHead - magHead)%AttitudeSensor._2PI < AttitudeSensor.MAX_HEADING_DIFF:
            
            imuHead = imuHead - self._imuAngleZOffset 
            heading = 0.7 * imuHead + 0.3 * magHead
            
        else:
            
            heading = magHead
            self._imuAngleZOffset = imuHead - magHead
        
        return math.degrees(heading)%360.0
    
    
    def start(self):
        
        self._imu.dmpInitialize()
        self._imu.setDMPEnabled(True)
        self._mag.initialize()
        
        self._imuPacketSize = self._imu.dmpGetFIFOPacketSize()
        
    
    def stop(self):
        
        self._imu.setDMPEnabled(False)
        self._imu.setSleepEnabled(True)
        self._mag.setMode(HMC5883L.HMC5883L_MODE_IDLE)


    def calibrate(self, calibTime=30):
        
        headX, headY,_ = self._readSensors()
        lastHeadX = maxHeadX = minHeadX = headX
        lastHeadY = maxHeadY = minHeadY = headY
        
        t0 = time.time()
        
        lpfComp = 1.0 - AttitudeSensor.MAGNET_CALIB_LPF_ALPHA
        
        while time.time() - t0 < calibTime:
        
            headX, headY,_ = self._readSensors()
                    
            filtHeadX = lpfComp * lastHeadX + AttitudeSensor.MAGNET_CALIB_LPF_ALPHA * headX
            filtHeadY = lpfComp * lastHeadY + AttitudeSensor.MAGNET_CALIB_LPF_ALPHA * headY
            
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
                
            time.sleep(AttitudeSensor.MAGNET_CALIB_PERIOD)
    
        offsetX = (minHeadX+maxHeadX)/2.0
        maxValX = maxHeadX - offsetX
        
        offsetY = (minHeadY+maxHeadY)/2.0
        maxValY = maxHeadY - offsetY
        
        self._magCalib = {"x": {"offset": offsetX, "max": maxValX}, "y":{"offset": offsetY, "max": maxValY}}


    def _normalizeHeadingComponents(self, headX, headY):
        
        normHeadX = (headX - self._magCalib["x"]["offset"])/self._magCalib["x"]["max"]
        normHeadY = (headY - self._magCalib["y"]["offset"])/self._magCalib["y"]["max"]
        
        return (normHeadX, normHeadY)
    
    
    def _readImuPacket(self):
    
        while self._imu.getIntStatus() < 2:
            time.sleep(0.001)

        fifoCount = self._imu.getFIFOCount()
        if fifoCount == 1024:
            self._imu.resetFIFO()
            fifoCount = 0
        
        while fifoCount < self._imuPacketSize:
            time.sleep(0.001)
            fifoCount = self._imu.getFIFOCount()
        
        packet = self._imu.getFIFOBlock()
        fifoCount = self._imu.getFIFOCount()
        while fifoCount > 0:
            packet += self._imu.getFIFOBlock()
            fifoCount = self._imu.getFIFOCount()
    
        return packet
    
    
    def _readSensors(self):
        
        imuPacket = self._readImuPacket()
        q = self._imu.dmpGetQuaternion(imuPacket)
        g = self._imu.dmpGetGravity(q)        
        ypr = self._imu.dmpGetYawPitchRoll(q, g)
        
        angles = [
            AttitudeSensor.PHYSICAL_MPU_SIGNS[0]*ypr[AttitudeSensor.PHYSICAL_MPU_AXES[0]], 
            AttitudeSensor.PHYSICAL_MPU_SIGNS[1]*ypr[AttitudeSensor.PHYSICAL_MPU_AXES[1]],
            AttitudeSensor.PHYSICAL_MPU_SIGNS[2]*ypr[AttitudeSensor.PHYSICAL_MPU_AXES[2]]
        ]
            
        magDict = self._mag.getHeading()
        magField = [
            AttitudeSensor.PHYSICAL_MPU_SIGNS[0]*magDict[AttitudeSensor.PHYSICAL_MAGNET_AXES[0]],
            AttitudeSensor.PHYSICAL_MPU_SIGNS[1]*magDict[AttitudeSensor.PHYSICAL_MAGNET_AXES[1]],
            AttitudeSensor.PHYSICAL_MPU_SIGNS[2]*magDict[AttitudeSensor.PHYSICAL_MAGNET_AXES[2]],
        ]
        
        cosX = math.cos(angles[0])
        sinX = math.sin(angles[0])
        cosY = math.cos(angles[1])
        sinY = math.sin(angles[1])
        
        headX = magField[0] * cosY + magField[1] * sinX * sinY + magField[2] * cosX * sinY
        headY = magField[1] * cosX - magField[2] * sinX

        return (headX, headY, angles)
    