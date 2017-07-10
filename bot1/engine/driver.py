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

    #Maximal wheel spin difference in relation to main throtle to turn. 
    MAX_DIRECTION_DIFF = 50.0
    
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

        throttle=throttle/2.0            

        if throttle != 0.0:
            
            leftThrottle = throttle \
                                if direction < 0.0 else \
                                    (throttle + (direction * Driver.MAX_DIRECTION_DIFF / 100.0))
            rightThrottle = throttle \
                                if direction > 0.0 else \
                                    (throttle - (direction * Driver.MAX_DIRECTION_DIFF / 100.0))

            
            #In case of backwards movement, throttles of each wheel must be swapped between them.
            if throttle < 0.0:
                temp = leftThrottle
                leftThrottle = rightThrottle
                rightThrottle = temp

            #logging.debug("({0},{1}) -> ({2},{3})".format(throttle, direction, leftThrottle, rightThrottle))

            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
            
        elif direction == 0.0:
            
            self._leftMotor.setNeutralThrottle()
            self._rightMotor.setNeutralThrottle()
            
        else:
            
            leftThrottle = throttle + (direction * Driver.MAX_DIRECTION_DIFF / 100.0)
            rightThrottle = throttle - (direction * Driver.MAX_DIRECTION_DIFF / 100.0)

            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
            
        self._throttle = throttle
        self._direction = direction        
        
        
    def getActualMotionVector(self):
        '''
        Calculates actual throttle and direction:
            Steering near the max throttle can reduce the effective throttle, 
            due to one of the wheels can not be reaching the maximum difference regarding the desired main throttle.
            
        @return: [throttle, direction]
        '''
        
        actualLeftThrottle = self._leftMotor.getThrottle()
        actualRightThrottle = self._rightMotor.getThrottle()
        throttle = (actualLeftThrottle + actualRightThrottle) / 2.0
        direction =  (throttle - actualRightThrottle) * 100.0 / Driver.MAX_DIRECTION_DIFF
        
        return [throttle, direction]
        
        
