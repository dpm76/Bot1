'''
Created on 11 nov. 2018

@author: david
'''
import logging
import time

from engine.driver import Driver
from piloting.pilot import BasicPilot
from sensor.imu6050 import Imu6050


logging.basicConfig(level=logging.DEBUG)

def turnTo(pilot, imu, angle):
    
    logging.info("Turn target: {0}°".format(angle))
    pilot.turnTo(angle)
    logging.info("Angle after turn: {0:.3f}°".format(imu.readAngleZ()))    
    time.sleep(1)


imu = Imu6050()
driver = Driver.createForRobot()

logging.info("Initializing IMU")
imu.start()
logging.info("Initializing driver")
driver.start()

pilot = BasicPilot(driver, imu)

try:
    logging.info("Start")
    turnTo(pilot, imu, 45.0)
    turnTo(pilot, imu, 315.0)
    turnTo(pilot, imu, 0.0)
    turnTo(pilot, imu, 180.0)
    turnTo(pilot, imu, 270.0)
    turnTo(pilot, imu, 0.0)
    logging.info("Finish")

finally:
    logging.info("Stopping driver")
    driver.stop()
    logging.info("Stopping IMU")
    imu.stop()
    