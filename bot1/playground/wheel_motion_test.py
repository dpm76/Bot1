'''
Created on 5 nov. 2018

@author: david
'''

import time

from sensor.wheel import WheelMotion
from engine.motor import Motor

THROTTLE = 15
MAX_STEPS = 10
TIMEOUT = 0.1

sensor = WheelMotion(67)
motor = Motor(1)

motor.start()

try:
    sensor.start()
    motor.setThrottle(THROTTLE)
    steps = 0
    while steps < MAX_STEPS:
        steps = sensor.getTravelSteps()
        print("steps = {0}".format(steps))
        time.sleep(TIMEOUT)
    motor.setNeutralThrottle()
    print("Total steps = {0}".format(sensor.getTravelSteps()))
    sensor.stop()
    time.sleep(1)
    sensor.start()
    motor.setThrottle(-THROTTLE)
    steps = 0
    while steps < MAX_STEPS:
        steps = sensor.getTravelSteps()
        print("steps = {0}".format(steps))
        time.sleep(TIMEOUT)
    motor.setNeutralThrottle()
    print("Total steps = {0}".format(sensor.getTravelSteps()))
    sensor.stop()
    
finally:
    motor.stop()
    sensor.stop()

