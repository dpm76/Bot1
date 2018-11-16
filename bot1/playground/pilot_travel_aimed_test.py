'''
Created on 6 nov. 2018

@author: david
'''
import logging
import time

from engine.driver import Driver
from piloting.pilot import BasicPilot, PilotState
from sensor.wheel import WheelMotion


logging.basicConfig(level=logging.INFO)

def waitPilot(pilot):
    
    while pilot.getState() != PilotState.Stopped:
        time.sleep(1)
        

TRAVEL_THROTTLE = 30.0

driver = Driver.createForRobot()
wheelSensor = WheelMotion(67)
pilot = BasicPilot(driver).setWheelMotionSensor(wheelSensor)

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
    
