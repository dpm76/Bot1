'''
Created on 27 oct. 2018

@author: david
'''

import logging
import time
from engine.driver import Driver 

class AutoPilot(object):
    
    def __init__(self, driver):
        
        self._driver = driver
        

    def drive(self, throttle, timespan):
        
        self._driver.setNeutral()
        self._driver.setMode(Driver.MODE_NORMAL)
        self._driver.setDirection(0.0)
        self._driver.setThrottle(throttle)
        time.sleep(timespan)
        self._driver.setNeutral()
        
    
    def rotate(self, direction, timespan):
        
        self._driver.setNeutral()
        self._driver.setMode(Driver.MODE_ROTATE)
        driver.setThrottle(0.0)
        self._driver.setDirection(direction)
        time.sleep(timespan)
        self._driver.setNeutral()
        


logging.basicConfig(level=logging.DEBUG)

driver = Driver.createForTesting()
#driver = Driver.createForRobot()
pilot = AutoPilot(driver)
driver.start()

logging.info("**** Forwards ****")
pilot.drive(-30.0, 2)
logging.info("**** Backwards ****")
pilot.drive(30.0, 2)
logging.info("**** Rotate ****")
pilot.rotate(30.0, 2)
logging.info("**** Forwards ****")
pilot.drive(-30.0, 2)
logging.info("**** Backwards ****")
pilot.drive(30.0, 2)
logging.info("**** Rotate ****")
pilot.rotate(-30.0, 2)
logging.info("**** Forwards ****")
pilot.drive(-30.0, 2)
logging.info("**** Backwards ****")
pilot.drive(30.0, 2)


driver.stop()
