'''
Created on 30 oct. 2018

@author: david
'''

import logging
import time

from engine.driver import Driver
from sensor.imu_dummy import ImuDummy


logging.basicConfig(level=logging.DEBUG)

targetAngle = 90.0

driver = Driver.createForTesting()
imu = ImuDummy(0.0)

imu.start()
driver.start()

try:
    driver.setNeutral()
    driver.setMode(Driver.MODE_ROTATE)
    currentAngle = imu.readAngleZ()
    direction = -30.0 if (targetAngle-currentAngle)%360.0 < 180.0 else 30.0 
    driver.setDirection(direction)
    while abs(targetAngle-currentAngle) < 1.0:
        currentAngle = imu.readAngleZ()
        time.sleep(0.1)
        
    driver.setNeutral()

finally:
    driver.stop()
    imu.stop()
    