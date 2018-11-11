'''
Created on 06/11/2018

@author: david
'''
from enum import Enum, unique
import time

from engine.driver import Driver


@unique
class PilotState(Enum):

    Stopped = 0
    Travelling = 1
    Rotating = 2


class BasicPilot(object):
    
    #TODO: 20181110 DPM: The following values should be taken from a sort of configuration
    ROTATION_MAX_THROTTLE = 40.0
    ROTATION_MIN_THROTTLE = 25.0        
    ROTATION_PRECISION_DEGREES = 5.0
    ROTATION_PID_PERIOD = 0.02    
    ROTATION_KP = 0.05
    ROTATION_KI = 0.02
    ROTATION_KD = 0.05
    
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
    
    
    def turnTo(self, targetAngle):
        
        if self._state == PilotState.Stopped and self._imu != None:
            
            self._driver.setNeutral()
            self._driver.setMode(Driver.MODE_ROTATE)
            self._imu.updateGyroTime()
            lastTime = time.time()
            currentAngle = self._imu.readAngleZ()
            err1 = (targetAngle-currentAngle)%360.0
            err2 = (currentAngle-targetAngle)%360.0
            integral = 0.0
            lastError = 0.0
            if err1 < err2:
                err = -err1
            else:
                err = err2
            while abs(err) > BasicPilot.ROTATION_PRECISION_DEGREES:
                time.sleep(BasicPilot.ROTATION_PID_PERIOD)
                currentTime = time.time()
                currentAngle = self._imu.readAngleZ()
                err1 = (targetAngle-currentAngle)%360.0
                err2 = (currentAngle-targetAngle)%360.0
                if err1 < err2:
                    err = -err1
                    minThrottle = -BasicPilot.ROTATION_MIN_THROTTLE
                else:
                    err = err2
                    minThrottle = BasicPilot.ROTATION_MIN_THROTTLE
        
                dt = currentTime - lastTime
                integral += err * dt
                deriv = (err - lastError) / dt
                direction = minThrottle + (BasicPilot.ROTATION_KP * err) + (BasicPilot.ROTATION_KI * integral) + (BasicPilot.ROTATION_KD * deriv)
                lastTime = currentTime
                lastError = err
  
                if direction > BasicPilot.ROTATION_MAX_THROTTLE:
                    direction = BasicPilot.ROTATION_MAX_THROTTLE
                elif direction < -BasicPilot.ROTATION_MAX_THROTTLE:
                    direction = -BasicPilot.ROTATION_MAX_THROTTLE
                self._driver.setDirection(direction)

            self._driver.setNeutral()
                    
        
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
    