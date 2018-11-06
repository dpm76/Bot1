'''
Created on 5 nov. 2018

@author: david
'''

import time

from sensor.wheel import WheelMotion
from engine.motor import Motor

THROTTLE = 80.0
MAX_STEPS = 20
TIMEOUT = 0.02

done = False

def onStep():
    
    if sensor.getTravelSteps() >= MAX_STEPS:
        global done
        done = True
        

def travel(throttle):

    global done

    sensor.start()    
    done = False
    motor.setThrottle(throttle)
    while not done:
        time.sleep(TIMEOUT)    
    print("Total steps = {0}".format(sensor.getTravelSteps()))
    sensor.stop()


sensor = WheelMotion(67)
sensor.onStep += onStep
motor = Motor(1)

motor.start()

try:
     
    travel(THROTTLE)
    travel(THROTTLE/2.0)
    travel(THROTTLE/4.0)
    motor.setNeutralThrottle()
    time.sleep(1)
        
    travel(-THROTTLE)
    travel(-THROTTLE/2.0)
    travel(-THROTTLE/4.0)
    motor.setNeutralThrottle()
    time.sleep(1)
    
finally:
    motor.stop()
    sensor.stop()

