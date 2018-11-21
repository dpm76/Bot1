'''
Created on 06/11/2018

@author: david
'''
from enum import Enum, unique
import time
import logging

from engine.driver import Driver


@unique
class PilotState(Enum):

    Stopped = 0
    Travelling = 1
    Rotating = 2


class BasicPilot(object):
    
    PID_PERIOD = 0.02
    
    #TODO: 20181110 DPM: The following values should be taken from a sort of configuration
    ROTATION_MAX_DIRECTION = 90.0
    ROTATION_MIN_DIRECTION = 25.0        
    ROTATION_PRECISION_DEGREES = 5.0
    ROTATION_KP = 0.05
    ROTATION_KI = 0.02
    ROTATION_KD = 0.05
    
    TRAVEL_MAX_DIRECTION = 50.0
    TRAVEL_AIMED_KP = 3.0
    TRAVEL_AIMED_KI = 1.0
    TRAVEL_AIMED_KD = 0.0
    
    def __init__(self, driver):
        
        self._driver = driver
        self._imu = None
        self._wheelMotionSensor = None        
        
        self._state = PilotState.Stopped
        
        self._travelStepsTarget = 0
        self._lastDirectionError = 0.0
        
         
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
    
    
    def _stabilizeDirection(self, targetAngle, minDir, maxDir, kp, ki, kd, endCondition, invertDirection=False):
        
        self._imu.updateGyroTime()
        lastTime = time.time()
        currentAngle = self._imu.readAngleZ()
        err1 = (targetAngle-currentAngle)%360.0
        err2 = (currentAngle-targetAngle)%360.0
        integral = 0.0        
        if err1 < err2:
            self._lastDirectionError = -err1
        else:
            self._lastDirectionError = err2
            
        while not endCondition():
            time.sleep(BasicPilot.PID_PERIOD)            
            currentTime = time.time()
            currentAngle = self._imu.readAngleZ()
            err1 = (targetAngle-currentAngle)%360.0
            err2 = (currentAngle-targetAngle)%360.0
            if err1 < err2:
                err = -err1
                minDirection = -minDir
            else:
                err = err2
                minDirection = minDir
                
            logging.debug("Stabilization error: {0:.3f}".format(err))
        
            dt = currentTime - lastTime
            integral += err * dt
            deriv = (err - self._lastDirectionError) / dt
            direction = minDirection + (kp * err) + (ki * integral) + (kd * deriv)
            lastTime = currentTime
            self._lastDirectionError = err
        
            if direction > maxDir:
                direction = maxDir
            elif direction < -maxDir:
                direction = -maxDir
            
            if invertDirection:
                direction = -direction
            
            logging.debug("Direction: {0:.3f}".format(direction))
            self._driver.setDirection(direction)
            
        logging.debug("Stabilization finished")


    
    def travelSteps(self, steps, throttle):
        
        if self._state == PilotState.Stopped and self._wheelMotionSensor != None:
            self._driver.setNeutral()
            self._driver.setMode(Driver.MODE_NORMAL)
            self._travelStepsTarget = steps
            self._wheelMotionSensor.resetStepCounter()
            self._state = PilotState.Travelling
            self._driver.setThrottle(throttle)            
        
        elif self._state != PilotState.Stopped:
            raise Exception("The robot should be stopped first.")
            
        else:
            raise Exception("There is no wheel motion sensor!")
        
    
    def travelAimedSteps(self, steps, throttle, aimAngle):
        
        if self._imu != None:
            self.travelSteps(steps, throttle)
            self._stabilizeDirection(aimAngle,\
                                     0.0,\
                                     BasicPilot.TRAVEL_MAX_DIRECTION,\
                                     BasicPilot.TRAVEL_AIMED_KP,\
                                     BasicPilot.TRAVEL_AIMED_KI,\
                                     BasicPilot.TRAVEL_AIMED_KD,\
                                     lambda: self._state == PilotState.Stopped,
                                     throttle < 0.0)

        else:
            raise Exception("There is no IMU sensor!")
    
    
    def turnTo(self, targetAngle):
        
        if self._state == PilotState.Stopped and self._imu != None:
            
            self._driver.setNeutral()
            self._driver.setMode(Driver.MODE_ROTATE)
            
            self._stabilizeDirection(targetAngle,\
                                     BasicPilot.ROTATION_MIN_DIRECTION,\
                                     BasicPilot.ROTATION_MAX_DIRECTION,\
                                     BasicPilot.ROTATION_KP,\
                                     BasicPilot.ROTATION_KI,\
                                     BasicPilot.ROTATION_KD,\
                                     lambda: abs(self._lastDirectionError) < BasicPilot.ROTATION_PRECISION_DEGREES)

            self._driver.setNeutral()
                    
        
        elif self._state != PilotState.Stopped:
            raise Exception("The robot should be stopped first.")
        
        else:
            raise Exception("There is no IMU sensor!")
    
    
    def turn(self, angle):
    
        if self._imu != None:
        
            currentAngle = self.getCurrentAngle()
            targetAngle = (currentAngle + angle) % 360.0
            self.turnTo(targetAngle)
        
        else:
            raise Exception("There is no IMU sensor!")
    
    
    def getCurrentAngle(self):
            
        self._imu.updateGyroTime()
        currentAngle = self._imu.readAngleZ()
        
        return currentAngle
        
    
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
    
