'''
Created on 29 oct. 2018

@author: david
'''

from engine.motor import Motor
from sensor.imu6050 import Imu6050
from time import sleep

MAX_THROTTLE = 30.0
INC_THROTTLE = 5.0

motor = Motor(0)
imu = Imu6050()

imu.start()
motor.start()

throttle = 0.0
angSpeed = 0.0

print("Start motor callibration")

try:

    while throttle < MAX_THROTTLE and angSpeed < 1.0:
    
        throttle += INC_THROTTLE
        print("Throttle = {0}".format(throttle))
        motor.setThrottle(throttle)
        sleep(0.1)
        angSpeed = imu.readAngSpeedZ()
    
    if throttle < MAX_THROTTLE:
        
        print("Motion detected with throttle = {0}".format(throttle))
        
    else:
        
        print("The motor get no motion!")

finally:

    motor.stop()
    imu.stop()
