# -*- coding: utf-8 -*-
'''
Created on 04/03/2016

@author: david
'''

from copy import deepcopy
import json
import logging
from math import degrees
from os import path
import time

from sensor.pycomms.mpu6050 import MPU6050
from sensor.vector import Vector
import sensor.imu6050_defs as reg

class Imu6050Dmp(object):
    '''
    IMU-6050 using the DMP (digital motion processing) feature
    '''

    CALIBRATION_FILE_PATH = "./sensor-calibration.json"
    GRAVITY = 9.807

    def __init__(self):
        
        self._imu = MPU6050(channel=1)

        self._packetSize = 0 #Assigned on start up
        self._angleOffset = [0.0]*3 #radians
        self._gravityOffset = [0.0]*3 #g
        
        self._angleSpeeds = [0.0]*3 #degrees
        self._angles = [0.0]*3 #radians
        self._accels = [0.0]*3 #g
        
        self._readTime = time.time()
        
        self._packet = None
    

    def readAngleSpeeds(self):

        angleSpeeds = [degrees(angleSpeed) for angleSpeed in self._angleSpeeds]

        return angleSpeeds

    
    def readAngles(self):
        
        angles = [degrees(angle) for angle in self._angles]

        return angles


    def readDeviceAngles(self):
        
        deviceAngles = [0.0]*3
        for index in range(3):
            deviceAngles[index] = self._angles[index] - self._angleOffset[index]

        angles = [degrees(angle) for angle in deviceAngles]

        return angles
    
    def readAccels(self):
        
        accels = [0.0]*3
        for index in range(3):
            accels[index] = (self._accels[index] - self._gravityOffset[index]) * Imu6050Dmp.GRAVITY
        
        return accels

    
    def updateGyroTime(self):
            
        self._readTime = time.time()
        

    def _readPacket(self):
    
        while self._imu.getIntStatus() < 2:
            time.sleep(0.001)

        fifoCount = self._imu.getFIFOCount()
        if fifoCount == 1024:
            self._imu.resetFIFO()
            fifoCount = 0
        
        while fifoCount < self._packetSize:
            time.sleep(0.001)
            fifoCount = self._imu.getFIFOCount()
        
        self._packet = self._imu.getFIFOBlock()
        fifoCount = self._imu.getFIFOCount()
        while fifoCount > 0:
            self._packet += self._imu.getFIFOBlock()
            fifoCount = self._imu.getFIFOCount()
    

    def refreshState(self):
        
        self._readPacket()
        packet = deepcopy(self._packet)
        
        q = self._imu.dmpGetQuaternion(packet)
        g = self._imu.dmpGetGravity(q)
        
        ypr = self._imu.dmpGetYawPitchRoll(q, g)
        previousAngles = self._angles
        self._angles = [ypr["pitch"], ypr["roll"], ypr["yaw"]]
        
        previousTime = self._readTime
        self._readTime = time.time()
        dt = self._readTime - previousTime        
        
        for index in range(3):
            self._angleSpeeds[index] = (self._angles[index] - previousAngles[index]) / dt

        accelRaw = self._imu.dmpGetAccel(packet)
        
        linearAccel = self._imu.dmpGetLinearAccel(accelRaw, g)
        self._accels = Vector.rotateVector3D(linearAccel, self._angles)


    def readAngleZ(self):
        
        self._readPacket()        
        
        q = self._imu.dmpGetQuaternion(self._packet)
        g = self._imu.dmpGetGravity(q)
        
        ypr = self._imu.dmpGetYawPitchRoll(q, g)        
        self._angles = [ypr["pitch"], ypr["roll"], ypr["yaw"]]
        angleZ = degrees(self._angles[2])
        if angleZ < 0.0:
            angleZ += 360.0
        
        return angleZ
        
        
    def _readRawGyroX(self):
        
        return self._readWordHL(reg.GYRO_XOUT)
    
    
    def _readRawGyroY(self):
        
        return self._readWordHL(reg.GYRO_YOUT)
    
    
    def _readRawGyroZ(self):
        
        return self._readWordHL(reg.GYRO_ZOUT)
    
    
    def start(self):

        logging.info("Using IMU-6050 (DMP).")
        
        self._imu.dmpInitialize()
        self._imu.setDMPEnabled(True)

        # Get expected DMP packet size for later comparison
        self._packetSize = self._imu.dmpGetFIFOPacketSize()
        
        self.calibrate(True)
        
    
    def calibrate(self, ignoreConfig=False):
        '''
        Calibrates sensor.
        @params ignoreConfig: Forces to calibrate from sensor, ignoring config file.
        '''
    
        logging.info("Calibrating...")
        time.sleep(1)
        self._imu.resetFIFO()
        
        #Wait for next packet
        time.sleep(0.1)
        
        self._readPacket()
        packet = deepcopy(self._packet)
        
        q = self._imu.dmpGetQuaternion(packet)
        g = self._imu.dmpGetGravity(q)
        
        if not ignoreConfig and path.exists(Imu6050Dmp.CALIBRATION_FILE_PATH):

            logging.info("Reading calibration from file '{0}'.".format(Imu6050Dmp.CALIBRATION_FILE_PATH)) 
            
            with open(Imu6050Dmp.CALIBRATION_FILE_PATH, "r") as calibrationFile:
                serializedCalibration = " ".join(calibrationFile.readlines())
                calibrationFile.close()
                
            self._angleOffset = json.loads(serializedCalibration)
            
        else:
                        
            ypr = self._imu.dmpGetYawPitchRoll(q, g)
            self._angleOffset = [ypr["pitch"], ypr["roll"], ypr["yaw"]]
            
            #Save calibration
            serializedCalibration = json.dumps(self._angleOffset)
            with open(Imu6050Dmp.CALIBRATION_FILE_PATH, "w+") as calibrationFile:
                calibrationFile.write(serializedCalibration + "\n")
                calibrationFile.close()
        
        logging.info("Sensor's angles: ({0}, {1}, {2})".format(*[degrees(angle) for angle in self._angleOffset]))
        
        accelRaw = self._imu.dmpGetAccel(packet)
        
        linearAccel = self._imu.dmpGetLinearAccel(accelRaw, g)
        self._gravityOffset = Vector.rotateVector3D(linearAccel, self._angleOffset)

        logging.info("... calibrated.")


    def stop(self):
        
        self._imu.setDMPEnabled(False)
        self._imu.setSleepEnabled(True)
    