'''
Created on 6 nov. 2018

@author: david
'''
import logging
import time

from engine.driver import Driver, StepMotor
from piloting.pilot import BasicPilot, PilotState
from sensor.wheel import WheelMotion
from sensor.imu6050dmp import Imu6050Dmp


logging.basicConfig(level=logging.DEBUG)

def waitPilot(pilot):
    
    while pilot.getState() != PilotState.Stopped:
        time.sleep(1)
        

TRAVEL_THROTTLE = 30.0

logging.info("Initializing IMU")
imu = Imu6050Dmp()
imu.start()
driver = Driver.createForRobot()
wheelSensor = WheelMotion(StepMotor._stepGpios[0])
pilot = BasicPilot(driver).setWheelMotionSensor(wheelSensor).setImuSensor(imu)

try:
    logging.info("Starting")
    wheelSensor.start()
    driver.start()

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 0°".format(angle))

    pilot.travelAimedSteps(100, -TRAVEL_THROTTLE, 0.0)
    pilot.turnTo(315.0)

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 315°".format(angle))

    pilot.travelAimedSteps(100, -TRAVEL_THROTTLE, 315.0)  

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 315°".format(angle))

    pilot.turnTo(0.0)

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 0°".format(angle))

    pilot.turnTo(135.0)

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 135°".format(angle))

    pilot.travelAimedSteps(100, -TRAVEL_THROTTLE, 135.0)  

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 135°".format(angle))

    pilot.turnTo(180.0)

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 180°".format(angle))

    pilot.travelAimedSteps(100, -TRAVEL_THROTTLE, 180.0)  

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 180°".format(angle))

    pilot.turnTo(90.0)

    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 90°".format(angle))


    pilot.turnTo(0.0)
    angle = imu.readAngleZ()
    logging.info("Heading: {0:.3f}°; expected 0°".format(angle))

finally:    
    driver.stop()
    wheelSensor.stop()
    imu.stop()
    logging.info("End")
