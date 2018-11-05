'''
Created on 5 nov. 2018

@author: david
'''

import time

from sensor.wheel import WheelMotion
from engine.motor import Motor

THROTTLE = 15
MAX_STEPS = 10
TIMEOUT = 1

done = False

def onStep():
    
    steps = sensor.getTravelSteps()
    print("steps = {0}".format(steps))
    if sensor.getTravelSteps() >= MAX_STEPS:        
        motor.setNeutralThrottle()        
        done = True
        

sensor = WheelMotion(67)
sensor.onStep += onStep
motor = Motor(1)

motor.start()

try:
     
    sensor.start()
    motor.setThrottle(THROTTLE)
    done = False
    while not done:        
        time.sleep(TIMEOUT)    
    print("Total steps = {0}".format(sensor.getTravelSteps()))
    sensor.stop()
    
    time.sleep(1)
        
    sensor.start()
    motor.setThrottle(-THROTTLE)
    done = False
    while not done:
        time.sleep(TIMEOUT)    
    print("Total steps = {0}".format(sensor.getTravelSteps()))
    sensor.stop()
    
finally:
    motor.stop()
    sensor.stop()

