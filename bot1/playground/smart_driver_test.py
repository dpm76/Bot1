from sensor.imu6050 import Imu6050
from engine.driver import StabilizedDriver
import time

imu = Imu6050()
driver = StabilizedDriver.createForTesting(imu)

driver.start()
driver.setThrottle(0.1)
time.sleep(5)
driver.setThrottle(10)
time.sleep(5)
driver.stop()


