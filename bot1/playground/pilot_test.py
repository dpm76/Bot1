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


logging.basicConfig(level=logging.INFO)

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

    logging.info("N")
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 0.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))

    logging.info("NW")
    pilot.turnTo(45.0)
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 45.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))
    
    logging.info("W")
    pilot.turnTo(90.0)
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 90.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))

    logging.info("SW")
    pilot.turnTo(135.0)
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 135.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))

    logging.info("S")
    pilot.turnTo(180.0)
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 180.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))

    logging.info("SE")
    pilot.turnTo(225.0)
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 225.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))
    
    logging.info("E")
    pilot.turnTo(270.0)
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 270.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))

    logging.info("NE")
    pilot.turnTo(315.0)
    waitPilot(pilot)    
    pilot.travelAimedSteps(80, -TRAVEL_THROTTLE, 315.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))

    pilot.turnTo(0.0)
    logging.info("current angle: {0:.3f}".format(imu.readAngleZ()))

finally:    
    driver.stop()
    wheelSensor.stop()
    imu.stop()
    logging.info("End")
