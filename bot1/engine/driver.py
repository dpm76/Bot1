# -*- coding: utf-8 -*-

'''
Created on 06/04/2015

@author: david
'''

from engine.motor import Motor, MotorDummy
import logging

class Driver(object):
    '''
    Controls a motor set
    '''

    #Thresholds for throttle ranges. For each range a different turning method will be used. 
    THROTTLE_RANGE_THRESHOLD_1 = 25.0
    THROTTLE_RANGE_THRESHOLD_2 = 75.0
    THROTTLE_RANGE_THRESHOLD_DIFF = THROTTLE_RANGE_THRESHOLD_2 - THROTTLE_RANGE_THRESHOLD_1 

    #Direction divisors to set the wheels spining at diferent speeds in order to turn the robot.  
    DIRECTION_DIV1 = 100.0
    DIRECTION_DIV2 = 400.0
    
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
        self.setMotionVector(throttle, self._direction)
        
    
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
        self.setMotionVector(self._throttle, direction)
        
    
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
        @param throttle: Throttle range is [-100, 100], where negative values mean backwards and positive ones mean forwards.
        @param direction: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''
        
        self._throttle = throttle
        self._direction = direction
        
        logging.debug("motion vector=(t:{0}, d:{1})".format(self._throttle, self._direction))
        
        if throttle != 0.0:
            
            modThrottle = abs(throttle)
        
            if modThrottle < Driver.THROTTLE_RANGE_THRESHOLD_1:
                
                if direction >= 0.0:
                    
                    leftThrottle = throttle + throttle * (direction/Driver.DIRECTION_DIV1)
                    rightThrottle = throttle
                    
                else:
                                
                    leftThrottle = throttle
                    rightThrottle = throttle - throttle * (direction/Driver.DIRECTION_DIV1)
                      
            elif Driver.THROTTLE_RANGE_THRESHOLD_1 <= modThrottle < Driver.THROTTLE_RANGE_THRESHOLD_2:
                
                if direction >= 0.0:
                    
                    leftThrottle = throttle + throttle * (direction/Driver.DIRECTION_DIV1) \
                        * ((Driver.THROTTLE_RANGE_THRESHOLD_2 - modThrottle) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                    rightThrottle = throttle - throttle * (direction/Driver.DIRECTION_DIV2) \
                        * ((modThrottle - Driver.THROTTLE_RANGE_THRESHOLD_1) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                    
                else:
                                
                    leftThrottle = throttle + throttle * (direction/Driver.DIRECTION_DIV2) \
                        * ((modThrottle - Driver.THROTTLE_RANGE_THRESHOLD_1) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                    rightThrottle = throttle - throttle * (direction/Driver.DIRECTION_DIV1) \
                        * ((Driver.THROTTLE_RANGE_THRESHOLD_2 - modThrottle) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
    
            else:
                
                if direction >= 0.0:
                    
                    leftThrottle = throttle
                    rightThrottle = throttle - throttle * (direction/Driver.DIRECTION_DIV2)
                    
                else:
                    
                    leftThrottle = throttle + throttle * (direction/Driver.DIRECTION_DIV2)
                    rightThrottle = throttle
                    
            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
    
        else:
            
            self._leftMotor.setNeutralThrottle()
            self._rightMotor.setNeutralThrottle()
        
        '''
        TODO: Spin robot when throttle is 0 
        else:
            
            leftThrottle = baseThrottle + (direction * Driver.MAX_DIRECTION_DIFF / 100.0)
            rightThrottle = baseThrottle - (direction * Driver.MAX_DIRECTION_DIFF / 100.0)

            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
        '''
            
        
