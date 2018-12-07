'''
Created on 12 nov. 2018

@author: david
'''
import logging
from threading import Thread
import time

from engine.motor import StepMotor

logging.basicConfig(level=logging.DEBUG)

def _doPoll(wheelSensor):    
    
    global running
    while running:
        stepSpeed = wheelSensor.getCurrentStepSpeed()
        logging.info("Current speed = {0:.3f} steps/s".format(stepSpeed))
        time.sleep(1)


def drive(motor, throttle, driveTime):
    
    targetSpeed = StepMotor.STEP_SPEED_MAX * throttle / 100.0
    logging.info("Throttle = {0}; Target speed = {1:.3f} step/s".format(throttle, targetSpeed))
    motor.setThrottle(throttle)
    time.sleep(driveTime)

    
MOTOR_ID = 1

motor = StepMotor(MOTOR_ID)
wheelSensor = motor.getWheelMotionSensor()


logging.info("Starting")

motor.start()

running = True

thread = Thread(target=_doPoll, args=[wheelSensor])
thread.start()

try:
    drive(motor, 50.0, 5)
    motor.setNeutralThrottle()
    time.sleep(3)
    drive(motor, -20.0, 5)
    drive(motor, -60.0, 5)
    motor.setNeutralThrottle()
    time.sleep(3)
    drive(motor, 20.0, 5)
    drive(motor, 60.0, 5)
    motor.setNeutralThrottle()
    time.sleep(3)
    drive(motor, -20.0, 5)
    drive(motor, 20.0, 5)
    motor.setNeutralThrottle()
    time.sleep(3)
    
finally:
    motor.stop()
    running = False
    if thread.isAlive():
        thread.join()
    logging.info("End")
