'''
Created on 6 nov. 2018

@author: david
'''
import time

from engine.driver import Driver
from piloting.pilot import BasicPilot, PilotState
from sensor.wheel import WheelMotion


def waitPilot(pilot):
    
    while pilot.getState() != PilotState.Stopped:
        time.sleep(1)
        

TRAVEL_THROTTLE = 30.0

driver = Driver.createForRobot()
wheelSensor = WheelMotion(67)
pilot = BasicPilot(driver).setWheelMotionSensor(wheelSensor)

try:
    driver.start()
    pilot.Travel(40, TRAVEL_THROTTLE)
    waitPilot(pilot)

finally:
    wheelSensor.stop()
    driver.stop()
