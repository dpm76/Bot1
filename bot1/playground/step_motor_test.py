'''
Created on 12 nov. 2018

@author: david
'''
import logging
from threading import Timer
import time

from engine.motor import StepMotor
from sensor.wheel import WheelMotion

logging.basicConfig(level=logging.INFO)

def _doPoll(wheelSensor):    
    
    stepSpeed = wheelSensor.getCurrentStepSpeed()
    logging.info("Current speed = {0:.3f} steps/s".format(stepSpeed))


def drive(motor, throttle, driveTime):
    
    logging.info("Throttle = {0}".format(throttle))
    motor.setThrottle(throttle)
    time.sleep(driveTime)
    

wheelSensor = WheelMotion(StepMotor._stepGpios[0])
motor = StepMotor(0, wheelSensor)


logging.info("Starting")

wheelSensor.start()
motor.start()

timer = Timer(1, _doPoll, wheelSensor)
timer.start()

try:
    drive(motor, 50.0, 15)        
    
finally:
    timer.cancel()
    motor.stop()
    wheelSensor.stop()
    logging.info("End")
