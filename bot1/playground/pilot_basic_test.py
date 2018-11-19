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

TRAVEL_LENGTH = 160

logging.basicConfig(level=logging.INFO)

def move(pilot, turnAngle):

    logging.info("Turning {0:.3f}°".format(turnAngle))
    pilot.turn(turnAngle)
    currentAngle = pilot.getCurrentAngle()
    logging.info("Travelling aimed to {0:.3f}°".format(currentAngle))
    pilot.travelAimedSteps(TRAVEL_LENGTH, -TRAVEL_THROTTLE, currentAngle)


TRAVEL_THROTTLE = 35.0

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

    move(pilot, 0.0)
    move(pilot, 45.0)
    #move(pilot, -45.0)
    #move(pilot, 90.0)
    #move(pilot, 90.0)
    
finally:    
    driver.stop()
    wheelSensor.stop()
    imu.stop()
    logging.info("End")
