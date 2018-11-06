'''
Created on 06/11/2018

@author: david
'''
from enum import Enum, unique

@unique
class PilotState(Enum):

    Stopped = 0
    Travelling = 1
    Rotating = 2


class BasicPilot(object):
        
    
    def __init__(self, driver):
        
        self._driver = driver
        self._imu = None
        self._wheelMotionSensor = None        
        
        self._state = PilotState.Stopped
        
        self._travelStepsTarget = 0
        
         
    def setImuSensor(self, imu):
        
        self._imu = imu
        
        return self
    
    
    def setWheelMotionSensor(self, sensor):
        
        if self._wheelMotionSensor != None:
            self._wheelMotionSensor.onStep -= self._onWheelStep
        
        self._wheelMotionSensor = sensor
        self._wheelMotionSensor.onStep += self._onWheelStep
        
        return self
    
    
    def getState(self):
        
        return self._state
    
    
    def travel(self, steps, throttle):
        
        if self._state == PilotState.Stopped and self._wheelMotionSensor != None:
            self._travelStepsTarget = steps
            self._wheelMotionSensor.resetStepCounter()
            self._state = PilotState.Travelling
            self._driver.setThrottle(throttle)            
        
        elif self._state != PilotState.Stopped:
            raise Exception("The robot should be stopped first.")
            
        else:
            raise Exception("There is no wheel motion sensor!")
    
    
    def rotate(self):
        
        if self._state == PilotState.Stopped and self._imu != None:
            #TODO: Implement rotatation
            
            pass
        
        elif self._state != PilotState.Stopped:
            raise Exception("The robot should be stopped first.")
        
        else:
            raise Exception("There is no IMU sensor!")
    
    
    def stop(self):
        
        self._driver.setNeutral()
        if self._state == PilotState.Travelling and self._wheelMotionSensor != None:
            self._travelStepsTarget = 0
            
        self._state = PilotState.Stopped
        
    
    def _onWheelStep(self):
        
        if self._state == PilotState.Travelling:
            
            steps = self._wheelMotionSensor.getTravelSteps()
            if steps >= self._travelStepsTarget:
                self.stop()
    