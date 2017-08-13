'''
Created on 13 ago. 2017

@author: david
'''
import sys

from engine.motor import Motor
from time import sleep
from threading import Thread

done = False
throttle = 0.0

def manualCalibration(idMotor="0", startThrottle="10.0"):

    global done
    global throttle
    
    throttle= float(startThrottle)

    thread = Thread(target=_doAccelerateMotor, args=(int(idMotor),))
    thread.start()
    
    try:    
        input("Press ENTER-key to finish...")        
        print("finish throttle={0}".format(throttle))
        
    finally:
        print("Finishing...")
        done=True
        thread.join(5)
        print("Done!")
        
        
def _doAccelerateMotor(idMotor):
    global throttle

    motor = Motor(idMotor)
    motor.start()
    
    try:        
        while not done:
            print("current throttle={0}".format(throttle))
            motor.setThrottle(throttle)
            sleep(0.5)
            throttle += 1.0            
            
    finally:
        motor.stop()


if __name__ == '__main__':
    manualCalibration(*sys.argv[1:])
    
