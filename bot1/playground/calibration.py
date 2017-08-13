'''
Created on 13 ago. 2017

@author: david
'''
from engine.motor import Motor
from time import sleep
from threading import Thread

done = False
throttle = 0.0

def manualCalibration():
    
    thread = Thread(target=_doAccelerateMotor, args=(0))
    thread.start()
    
    try:    
        input("Press ENTER-key to finish...")        
        print("finish throttle={0}".format(throttle))
        
    finally:
        done=True
        thread.join(1)
        
        
def _doAccelerateMotor(idMotor):

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
    manualCalibration()
    