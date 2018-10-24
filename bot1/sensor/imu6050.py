# -*- coding: utf-8 -*-
'''
Created on 09/10/2018

@author: david
'''

import logging
import math
import time

import sensor.imu6050_defs as reg
from sensor.I2CSensor import I2CSensor

try:
    import smbus
    
except ImportError:
    
    class smbus(object):
        @staticmethod
        def SMBus(channel):
            raise Exception("smbus module not found!")


class Imu6050(I2CSensor):
    '''
    Gyro and accelerometer
    '''
    
    ADDRESS = 0x68
    GYRO2DEG = 250.0 / 32767.0 # +/- 250º/s mode
    ACCEL2G = 2.0 / 32767.0 # +/- 2g mode
    GRAVITY = 9.807 #m/s²
    PI2 = math.pi / 2.0
    ACCEL2MS2 = GRAVITY * ACCEL2G
    

    def __init__(self):
        '''
        Constructor
        '''
        
        self._setAddress(Imu6050.ADDRESS)
        self._bus = smbus.SMBus(1)
        
        self._gyroOffset = [0]*3
        self._lastReadGyroTime = time.time()
        self._lastReadAngles = [0.0]*3
        self._lastReadAngSpeed = [0.0]*3
        self._accOffset = [0]*3
    
    
    def _readRawGyroX(self):
        
        return self._readWordHL(reg.GYRO_XOUT)
    
    
    def _readRawGyroY(self):
        
        return self._readWordHL(reg.GYRO_YOUT)
    
    
    def _readRawGyroZ(self):
        
        return self._readWordHL(reg.GYRO_ZOUT)
    
    
    def _readAngSpeed(self, reg, index):

        return (self._readWordHL(reg) - self._gyroOffset[index]) * Imu6050.GYRO2DEG
    
    
    def readAngSpeedX(self):
        '''
        Angle-speed of X axis
        
        return: angle  as degrees per second
        '''
        
        return self._readAngSpeed(reg.GYRO_XOUT, 0)


    def readAngSpeedY(self):
        '''
        Angle-speed of Y axis
        
        return: angle  as degrees per second
        '''
        
        return self._readAngSpeed(reg.GYRO_YOUT, 1)


    def readAngSpeedZ(self):
        '''
        Angle-speed of Z axis
        
        return: angle  as degrees per second
        '''
        
        return self._readAngSpeed(reg.GYRO_ZOUT, 2)


    def readAngleSpeeds(self):
        '''
        Read all angle-speed at once
        
        return: Array of angle-speed as degrees per second
        '''

        return [
            self._readAngSpeedX(),
            self._readAngSpeedY(),        
            self._readAngSpeedZ()
        ]


    def readAngleZ(self):
        '''
        Estimates Z-axis angle from gyro
        
        return: angle as degrees
        '''
        
        currentTime = time.time()
        angSpeedZ = self.readAngSpeedZ()        
        dt2 = (currentTime - self._lastReadGyroTime) / 2.0
        angleZ = (self._lastReadAngles[2] + (angSpeedZ + self._lastReadAngSpeed[2]) * dt2) % 360.0
        
        self._lastReadGyroTime = currentTime
        self._lastReadAngles[2] = angleZ
        self._lastReadAngSpeed[2] = angSpeedZ
        
        return angleZ


    def resetAngleZ(self):
        '''
        Set last read Z-axis angle as 0. It limits the angle drifting.
        '''
        
        self._lastReadAngles[2] = 0.0

    
    def _readRawAccel(self, reg):

        return self._readWordHL(reg)
    
    
    def _readRawAccelX(self):
        
        return self._readRawAccel(reg.ACC_XOUT)
    
    
    def _readRawAccelY(self):
        
        return self._readRawAccel(reg.ACC_YOUT)
    
    
    def _readRawAccelZ(self):
        
        return self._readRawAccel(reg.ACC_ZOUT)
   
    
    def readAccelY(self):
        '''
        Reads accel of Y-axis
        
        return: acceleration as m/s²
        '''
        
        self._readRawAccelY() * Imu6050.ACCEL2MS2
    
    
    def readAccels(self):
        '''
        Reads accels at once
        
        return: array of accelerations as m/s²
        '''

        return [
            self._readRawAccelX() * Imu6050.ACCEL2MS2,
            self._readRawAccelY() * Imu6050.ACCEL2MS2,
            self._readRawAccelZ() * Imu6050.ACCEL2MS2
        ]
    
    
    def updateGyroTime(self):
        '''
        Updates the gyro time with the current time.
        Should be performed just before the first read.
        '''
        
        self._lastReadGyroTime = time.time()
    
    
    def start(self):
        '''        
         Initializes sensor
        '''
        
        logging.info("Using IMU-6050.")

        #Initializes gyro
        self._bus.write_byte_data(self._address, reg.PWR_MGM1, reg.RESET)
        self._bus.write_byte_data(self._address, reg.PWR_MGM1, reg.CLK_SEL_X)
        #1kHz (as DPLF_CG_6) / (SMPLRT_DIV +1) => sample rate @50Hz)
        self._bus.write_byte_data(self._address, reg.SMPRT_DIV, 19)
        #DLPF_CFG_5: Low-pass filter @10Hz; analog sample rate @1kHz
        self._bus.write_byte_data(self._address, reg.CONFIG, reg.DLPF_CFG_5)
        self._bus.write_byte_data(self._address, reg.GYRO_CONFIG, reg.GFS_250)
        self._bus.write_byte_data(self._address, reg.ACCEL_CONFIG, reg.AFS_2)
        self._bus.write_byte_data(self._address, reg.PWR_MGM1, 0)
        
        #TODO: 20181007 DPM: Set not used axis into standby
        
        #Wait for sensor stabilization
        time.sleep(1)
        
        self.calibrate()
    

    def calibrate(self):
        '''
        Calibrates sensor
        '''
        
        logging.info("Calibrating accelerometer...")
        self._accOffset = [0.0]*3
        
        i = 0
        while i < 100:

            self._accOffset[0] += self._readRawAccelX()
            self._accOffset[1] += self._readRawAccelY()
            self._accOffset[2] += self._readRawAccelZ()
            
            time.sleep(0.02)
            i+=1
        
        for index in range(3): 
            self._accOffset[index] /= float(i)
        
        
        #Calibrate gyro
        logging.info("Calibrating gyro...")
        self._gyroOffset = [0.0]*3
        
        i = 0
        while i < 100:
            
            self._gyroOffset[0] += self._readRawGyroX()
            self._gyroOffset[1] += self._readRawGyroY()
            self._gyroOffset[2] += self._readRawGyroZ()
            
            time.sleep(0.02)
            i += 1
            
        for index in range(3):
            self._gyroOffset[index] /= float(i) 
            
    
    def stop(self):
        '''
        Stops the sensor
        '''
        
        # Set sensor into standby mode
        self._bus.write_byte_data(self._address, reg.PWR_MGM1, reg.RESET)
        self._bus.write_byte_data(self._address, reg.PWR_MGM1, reg.SLEEP)
        self._bus.write_byte_data(self._address, reg.PWR_MGM1, 0)
    
