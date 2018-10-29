'''
Created on 29 oct. 2018

@author: david
'''

from engine.motor import Motor
from sensor.imu6050 import Imu6050
from time import sleep

MAX_THROTTLE = 30.0
THROTTLE_STEP = 5.0

def callibrate(motor, imu, throttleStep):

    throttle = 0.0
    angSpeed = 0.0
    
    motor.setNeutralThrottle()

    while abs(throttle) < MAX_THROTTLE and angSpeed < 1.0:
    
        throttle += throttleStep
        print("Throttle = {0}".format(throttle))
        motor.setThrottle(throttle)
        sleep(0.1)
        angSpeed = imu.readAngSpeedZ()
    
    motor.setNeutralThrottle()
    if abs(throttle) >= MAX_THROTTLE:
        
        raise Exception("The motor get no motion!")
    
    return throttle
        

motor = Motor(0)
imu = Imu6050()

print("Init IMU")
imu.start()
print("Init motor")
motor.start()

throttle = 0.0
angSpeed = 0.0

print("Start motor callibration")

try:

    print("fordwards")
    accThrottle = 0.0
    for i in range(3):
        throttle = callibrate(motor, imu, THROTTLE_STEP)
        print("pass {0}: min throttle = {1}".format(i, throttle))
        accThrottle += throttle
        
    avgThrottle = accThrottle / i
    print("avg throttle = {0}".format(avgThrottle))
    
    print("backwards")
    accThrottle = 0.0
    for i in range(3):
        throttle = callibrate(motor, imu, -THROTTLE_STEP)
        print("pass {0}: min throttle = {1}".format(i, throttle))
        accThrottle += throttle
        
    avgThrottle = accThrottle / i
    print("avg throttle = {0}".format(avgThrottle))

finally:

    motor.stop()
    imu.stop()
