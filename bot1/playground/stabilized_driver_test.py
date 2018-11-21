#from sensor.imu6050 import Imu6050
from sensor.imu_dummy import ImuDummy
from engine.driver import StabilizedDriver
import logging
import time

logging.basicConfig(level=logging.DEBUG)

imu = ImuDummy([0.0]*3)
driver = StabilizedDriver.createForTesting(imu)

driver.start()
driver.setThrottle(1.0)
time.sleep(1)
logging.info("**** Direction right ****")
driver.setDirection(50.0)
time.sleep(1)
logging.info("**** Direction left ****")
driver.setDirection(-50.0)
time.sleep(1)
logging.info("**** Change PID KP ****")
driver.setProportionalPidConstant(2.0)
time.sleep(1)
logging.info("**** Change to rear ****")
driver.setThrottle(-1.0)
time.sleep(1)
logging.info("**** Change PID KP ****")
driver.setProportionalPidConstant(1.0)
time.sleep(1)
logging.info("**** Direction right ****")
driver.setDirection(50.0)
time.sleep(1)
logging.info("**** Direction left ****")
driver.setDirection(-50.0)
time.sleep(1)
driver.stop()
