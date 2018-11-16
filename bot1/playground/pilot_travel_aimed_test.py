'''
Created on 6 nov. 2018

@author: david
'''
import logging
import time

from engine.driver import Driver, StepMotor
from piloting.pilot import BasicPilot, PilotState
from sensor.wheel import WheelMotion
from sensor.imu6050 import Imu6050


logging.basicConfig(level=logging.DEBUG)

def waitPilot(pilot):
    
    while pilot.getState() != PilotState.Stopped:
        time.sleep(1)
        

TRAVEL_THROTTLE = 30.0

logging.info("Initializing IMU")
imu = Imu6050()
imu.start()
driver = Driver.createForRobot()
wheelSensor = WheelMotion(StepMotor._stepGpios[0])
pilot = BasicPilot(driver).setWheelMotionSensor(wheelSensor).setImuSensor(imu)

try:
    logging.info("Starting")
    wheelSensor.start()
    driver.start()
    logging.info("Forwards")
    pilot.travelAimedSteps(40, TRAVEL_THROTTLE, 0.0)
    waitPilot(pilot)
    logging.info("Backwards")
    pilot.travelAimedSteps(40, -TRAVEL_THROTTLE, 0.0)
    waitPilot(pilot)

finally:
    logging.info("Finish")
    driver.stop()
    wheelSensor.stop()
    imu.stop()
