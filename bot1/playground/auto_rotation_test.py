'''
Created on 30 oct. 2018

@author: david
'''

import logging
import time

from engine.driver import Driver
#from sensor.imu_dummy import ImuDummy
from sensor.imu6050 import Imu6050


logging.basicConfig(level=logging.DEBUG)

MAX_THROTTLE = 40.0

PK = 0.05
PI = 0.01

def turnTo(targetAngle, imu, driver):

    driver.setNeutral()
    driver.setMode(Driver.MODE_ROTATE)
    imu.updateGyroTime()
    lastTime = time.time()
    currentAngle = imu.readAngleZ()
    err1 = (targetAngle-currentAngle)%360.0
    err2 = (currentAngle-targetAngle)%360.0
    integral = 0.0
    if err1 < err2:
        err = err1
    else:
        err = err2
    while err > 5.0:
        currentTime = time.time()
        currentAngle = imu.readAngleZ()
        logging.debug("current angle = {0:.3f}°".format(currentAngle))
        err1 = (targetAngle-currentAngle)%360.0
        logging.debug("current err1 = {0:.3f}°".format(err1))
        err2 = (currentAngle-targetAngle)%360.0
        logging.debug("current err2 = {0:.3f}°".format(err2))
        if err1 < err2:
            err = -err1
        else:
            err = err2

        dt = currentTime - lastTime
        integral += err * dt
        direction = (PK * err) + (PI * integral)
        lastTime = currentTime
            
        if direction > MAX_THROTTLE:
            direction = MAX_THROTTLE
        elif direction < -MAX_THROTTLE:
            direction = -MAX_THROTTLE
        logging.debug("direction = {0}".format(direction))
        driver.setDirection(direction)        
        time.sleep(0.1)
        
    logging.info("Target reached")
    driver.setNeutral()


#driver = Driver.createForTesting()
#imu = ImuDummy(0.0)
driver = Driver.createForRobot()
imu = Imu6050()

logging.info("Init IMU")
imu.start()
logging.info("Init driver")
driver.start()

try:
    
    turnTo(45.0, imu, driver)
    time.sleep(1)
    turnTo(315.0, imu, driver)

finally:
    driver.stop()
    imu.stop()
    