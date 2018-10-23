# -*- coding: utf-8 -*-

'''
Created on 06/04/2015

@author: david
'''

import logging

from engine.motor import Motor, MotorDummy
from stabilization.pid import Pid


class Driver(object):
    '''
    Controls a motor set
    '''

    #Driver modes    
    MODE_NORMAL = 0
    MODE_ROTATE = 1

    #Thresholds for throttle ranges. For each range a different turning method will be used. 
    THROTTLE_RANGE_THRESHOLD_1 = 25.0
    THROTTLE_RANGE_THRESHOLD_2 = 75.0
    THROTTLE_RANGE_THRESHOLD_DIFF = THROTTLE_RANGE_THRESHOLD_2 - THROTTLE_RANGE_THRESHOLD_1 

    #Direction divisors to set the wheels spining at diferent speeds in order to turn the robot.  
    DIRECTION_DIV1 = 50.0
    DIRECTION_DIV2 = 200.0
    
    @staticmethod
    def createForRobot():
        '''
        Creates a new motor driver for robot context
        @return: The driver object
        '''
        
        driver = Driver()
        driver.setMotors(Motor(1), Motor(0))
        
        return driver
    

    @staticmethod
    def createForTesting():
        '''
        Creates a new motor driver for testing context
        @return: The driver object
        '''
        
        driver = Driver()
        driver.setMotors(MotorDummy(1), MotorDummy(0))
        
        return driver


    def __init__(self):
        '''
        Constructor
        '''
        
        self._leftMotor = None
        self._rightMotor = None
        
        self._throttle = 0.0
        self._direction = 0.0
        
        self._mode = Driver.MODE_NORMAL
        
               
    def setMotors(self, leftMotor, rightMotor):
        '''
        Set motors to be driven
        @param leftMotor: The left motor
        @param rightMotor: The right motor
        '''
        
        self._leftMotor = leftMotor
        self._rightMotor = rightMotor
        
        
    def start(self):
        '''
        Starts the driver        
        '''
        
        if self._leftMotor and self._rightMotor:
            self._leftMotor.start()
            self._rightMotor.start()
            
        else:
            raise Exception("Motors not assigned yet. Please, use setMotors() before start.")
            
    
    def stop(self):
        '''
        Stop the motors
        '''
        
        self.setNeutral()
        
        self._leftMotor.stop()
        self._rightMotor.stop()
        
    
    def setThrottle(self, throttle):
        '''
        Set the throttle.
        @param throttle: Throttle range is [-100, 100], where negative values mean backwards and positive ones mean forwards.        
        '''
        self.setMotionVector(throttle, self.getDirection())
        
    
    def getThrottle(self):
        '''
        Get the throttle.
        @return: Throttle range is [-100, 100], where negative values mean backwards and positive ones mean forwards.
        '''
        return self._throttle
    
    
    def setDirection(self, direction):
        '''
        Set the direction.
        @param direction: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''
        self.setMotionVector(self.getThrottle(), direction)
        
    
    def getDirection(self):
        '''
        Get the direction.
        @return: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''
        return self._direction
    

    def setNeutral(self):
        '''
        Set the motion to neutral (stopped). Throttle and direction will be zero. 
        '''
        self.setMotionVector(0.0, 0.0)


    def setMotionVector(self, throttle, direction):
        '''
        Set the motion vector (both, throttle and direction) directly.
        Actual effect depends on the current driving mode.
        
        @param throttle: Throttle range is [-100, 100], where negative values mean backwards and positive ones mean forwards.
        @param direction: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''

        self._throttle = throttle
        self._direction = direction
        
        logging.debug("motion vector=(t:{0}, d:{1})".format(self._throttle, self._direction))
        
        if self._mode == Driver.MODE_NORMAL:
            
            self._setMotionVectorOnNormalMode()

        else: #Driver.MODE_ROTATE
            
            self._setMotionVectorOnRotateMode()
       


    def _setMotionVectorOnNormalMode(self):
        '''
        Set the motion vector on normal driving mode.        
        '''
        
        if self._throttle != 0.0:
            
            modThrottle = abs(self._throttle)
        
            if modThrottle < Driver.THROTTLE_RANGE_THRESHOLD_1:
                
                if self._direction >= 0.0:
                    
                    leftThrottle = self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV1)
                    rightThrottle = self._throttle
                    
                else:
                                
                    leftThrottle = self._throttle
                    rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV1)
                      
            elif Driver.THROTTLE_RANGE_THRESHOLD_1 <= modThrottle < Driver.THROTTLE_RANGE_THRESHOLD_2:
                
                if self._direction >= 0.0:
                    
                    leftThrottle = self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV1) \
                        * ((Driver.THROTTLE_RANGE_THRESHOLD_2 - modThrottle) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                    rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV2) \
                        * ((modThrottle - Driver.THROTTLE_RANGE_THRESHOLD_1) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                    
                else:
                                
                    leftThrottle = self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV2) \
                        * ((modThrottle - Driver.THROTTLE_RANGE_THRESHOLD_1) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                    rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV1) \
                        * ((Driver.THROTTLE_RANGE_THRESHOLD_2 - modThrottle) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
    
            else:
                
                if self._direction >= 0.0:
                    
                    leftThrottle = self._throttle
                    rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV2)
                    
                else:
                    
                    leftThrottle = self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV2)
                    rightThrottle = self._throttle
                    
            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
    
        else:
            
            self._leftMotor.setNeutralThrottle()
            self._rightMotor.setNeutralThrottle()
            
            
    def _setMotionVectorOnRotateMode(self):
        '''
        Set the motion vector on rotate driving mode.        
        '''
        
        if self._direction != 0:
        
            leftThrottle = self._direction
            rightThrottle = -self._direction
    
            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
            
        else:
            
            self._leftMotor.setNeutralThrottle()
            self._rightMotor.setNeutralThrottle()
               
            
    def setMode(self, mode):
        '''
        Set driver mode
        
        @param mode: Driving mode. See Driver.MODE_*        
        '''
        
        if self._mode != mode:
            
            self.setNeutral()
            self._mode = mode
    
    
    def getMode(self):
        '''
        Get current driver mode
        
        @return: Any of Driver.MODE_*
        '''
        
        return self._mode


class StabilizedDriver(Driver):
    '''
    Controls the driver in a smarty way
    '''
    
    PID_PERIOD = 0.1 #seconds
    MAX_ANG_SPEED = 10.0 #degrees / second
    
    
    @staticmethod
    def createForRobot(imu):
        '''
        Creates a new motor driver for robot context
        @return: The driver object
        '''
        
        driver = StabilizedDriver(imu)
        driver.setMotors(Motor(1), Motor(0))
        
        return driver
    

    @staticmethod
    def createForTesting(imu):
        '''
        Creates a new motor driver for testing context
        @return: The driver object
        '''
        
        driver = StabilizedDriver(imu)
        driver.setMotors(MotorDummy(1), MotorDummy(0))
        
        return driver

    
    def __init__(self, sensor):
        '''
        Constructor
        
        @param sensor: IMU/MPU in order to know the device's attitude 
        '''
        
        super().__init__()
        self._sensor = sensor
        
        self._directionTarget = 0.0
        
        self._stabilizerPid = Pid(StabilizedDriver.PID_PERIOD, 1, self._readCurrentValues, self._setPidOutput, "Driver-PID")
        self._stabilizerPid.setProportionalConstants([1.0])
        self._stabilizerPid.setIntegralConstants([0.0])
        
    
    def _readCurrentValues(self):
        
        return [self._sensor.readAngSpeedZ()]
    
    
    def _setPidOutput(self, pidOuput):
        
        throttle = super().getThrottle()
        super().setMotionVector(throttle, pidOuput[0])
        
        
    def setMotionVector(self, throttle, direction):
        
        if super().getMode() == Driver.MODE_NORMAL:
            
            super().setMotionVector(throttle, super().getDirection())
            self._directionTarget = -direction if throttle > 0.0 else direction
            self._stabilizerPid.setTargets([self._directionTarget * StabilizedDriver.MAX_ANG_SPEED / 100.0])
            
            if throttle == 0.0 and self._stabilizerPid.isRunning():                
                self._stabilizerPid.stop()                
            elif throttle != 0.0 and not self._stabilizerPid.isRunning():                
                self._stabilizerPid.start()
                
        else:
            super().setMotionVector(throttle, direction)

    
    def getDirection(self):
        '''
        Get the direction.
        @return: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''
        return self._directionTarget
    
    
    def setMode(self, mode):
        
        super().setMode(mode)
        
        if super().getMode() == Driver.MODE_NORMAL and super().getThrottle() != 0.0 \
            and not self._stabilizerPid.isRunning():
            
            self._stabilizerPid.start()
            
        else:
            
            self._stabilizerPid.stop()
            
            
    def start(self):
        
        self._sensor.start()
        super().start()
        
        
    def stop(self):
        
        if self._stabilizerPid.isRunning():
            self._stabilizerPid.stop()
            
        super().stop()
        self._sensor.stop()
        