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
    wheelSensor.start()
    driver.start()
    pilot.travel(40, TRAVEL_THROTTLE)
    waitPilot(pilot)
    pilot.travel(40, -TRAVEL_THROTTLE)
    waitPilot(pilot)

finally:
    driver.stop()
    wheelSensor.stop()
    
