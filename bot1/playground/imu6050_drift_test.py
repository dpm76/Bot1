'''
Created on 18/11/2018

@author: david
'''
import logging
import time

from threading import Thread
from sensor.imu6050 import Imu6050


class AngleProvider(object):

    def __init__(self, period):
    
        self._imu = Imu6050()
        self._period = period

        self._angle = 0.0
        
        self._isRunning = False
        self._imuReadThread = None
        
        
    def start(self):
    
        self._imu.start()
        if self._imuReadThread == None or not self._imuReadThread.isAlive():
        
            self._isRunning = True
            self._imuReadThread = Thread(target=self._doImuRead)
            self._imuReadThread.start()
        
        
    def stop(self):
    
        if self._imuReadThread != None and self._imuReadThread.isAlive():

            self._isRunning = False
            self._imuReadThread.join()
        
        self._imu.stop()
        
        
    def readAngleZ(self):
    
        return self._angle
            
        
    def _doImuRead(self):
    
        self._imu.updateGyroTime()
        while self._isRunning:
        
            self._angle = self._imu.readAngleZ()
            time.sleep(self._period)



logging.basicConfig(level=logging.INFO)

def emulateStabilization(imu, seconds):
    
    logging.debug("{0:.3f}°".format(imu.readAngleZ()))
    initTime = time.time()
    ellapsedTime = 0.0
    while ellapsedTime < seconds:
        time.sleep(0.02)
        imu.readAngleZ()
        logging.debug("{0:.3f}°".format(imu.readAngleZ()))
        ellapsedTime = time.time() - initTime


def keepAngle(imu, angle):

    logging.info("Keep at {0:.3f}°".format(angle))
    emulateStabilization(imu, 10.0)
    logging.info("Angle after keeping: {0:.3f}".format(imu.readAngleZ()))


def turnToAngle(imu, angle):

    logging.info("Turn to {0:.3f}°".format(angle))
    emulateStabilization(imu, 3.0)
    logging.info("Angle after turning: {0:.3f}".format(imu.readAngleZ()))


def testAngle(imu, angle):

    turnToAngle(imu, angle)
    keepAngle(imu, angle)


TRAVEL_THROTTLE = 30.0

logging.info("Initializing IMU")
imu = AngleProvider(0.02)
imu.start()

try:
    logging.info("Starting")
    
    keepAngle(imu, 0.0)
    testAngle(imu, 45.0)
    testAngle(imu, 90.0)
    testAngle(imu, 45.0)
    testAngle(imu, 0.0)
    testAngle(imu, 45.0)
    testAngle(imu, 90.0)
    testAngle(imu, 45.0)
    turnToAngle(imu, 0.0)

finally:    
    imu.stop()
    logging.info("End")
