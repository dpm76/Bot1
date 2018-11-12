'''
Created on 29 oct. 2018

@author: david
'''

import logging
from time import sleep

from engine.motor import Motor
from sensor.imu6050 import Imu6050


logging.basicConfig(level=logging.INFO)

MAX_THROTTLE = 30.0
THROTTLE_STEP = 5.0
NUM_PASSES = 5

def callibrate(motor, imu, throttleStep):

    throttle = 0.0
    angSpeed = 0.0
    
    motor.setNeutralThrottle()
    sleep(0.5)

    while abs(throttle) < MAX_THROTTLE and abs(angSpeed) < 1.0:
    
        throttle += throttleStep
        motor.setThrottle(throttle)
        sleep(0.25)
        angSpeed = imu.readAngSpeedZ()
    
    motor.setNeutralThrottle()
    sleep(0.5)
    if abs(throttle) >= MAX_THROTTLE:
        
        raise Exception("The motor get no motion!")
    
    return throttle
        

def callibrateMotor(motor, imu):

    logging.info("Init motor")
    motor.start()

    throttle = 0.0

    try:

        logging.info("fordwards")
        accThrottle = 0.0
        for i in range(NUM_PASSES):
            throttle = callibrate(motor, imu, THROTTLE_STEP)
            logging.info("pass {0}: min throttle = {1}".format(i, throttle))
            accThrottle += throttle
        
        avgThrottle = accThrottle / float(NUM_PASSES)
        logging.info("avg throttle = {0}".format(avgThrottle))
    
        logging.info("backwards")
        accThrottle = 0.0
        for i in range(NUM_PASSES):
            throttle = callibrate(motor, imu, -THROTTLE_STEP)
            logging.info("pass {0}: min throttle = {1}".format(i, throttle))
            accThrottle += throttle
        
        avgThrottle = accThrottle / float(NUM_PASSES)
        logging.info("avg throttle = {0}".format(avgThrottle))

    finally:

        motor.stop()


imu = Imu6050()
motor0 = Motor(0)
motor1 = Motor(1)

logging.info("Init IMU")
imu.start()

try:

    logging.info("motor 0")
    callibrateMotor(motor0, imu)
    logging.info("motor 1")
    callibrateMotor(motor1, imu)

finally:
    
    imu.stop()
