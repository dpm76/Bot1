'''
Created on 13 ago. 2017

@author: david
'''

from engine.motor import Motor
from time import sleep
from threading import Thread

done = False
throttle = 0.0

def manualCalibration(idMotor=0, startThrottle=10.0):
    '''
    Calibrates motor manually.
    Starts with minimal throttle and the user press ENTER-key whenever the wheel begins to move.
    Then the current throttle corresponds to the minimal effective throttle.
    
    @param idMotor: Motor to be calibrated (default: 0).
    @param startThrottle: Minimal throttle (default: 10.0).
    '''

    global done
    global throttle
    
    throttle= startThrottle

    thread = Thread(target=_doAccelerateMotor, args=(idMotor,))
    thread.start()
    
    try:    
        print("Calibrating motor {0}.".format(idMotor))
        input("\tPress ENTER-key to finish...")        
        print("finish throttle={0}".format(throttle))
        
    finally:
        print("Finishing...")
        done=True
        thread.join(5)
        print("Done!")
        
        
def _doAccelerateMotor(idMotor):
    '''
    Increases motor's throttle until the thread is stopped.
    
    @param idMotor: Motor identificator.
    '''
    
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
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Motor calibration using manual method.")
    parser.add_argument("motorId", metavar="motor-ID", type=int, nargs="?", default=0,
                    help="Motor to be calibrated (default: 0).")
    parser.add_argument("minThrottle", metavar="min-throttle", type=float, nargs="?", default = 10.0,                   
                    help="Minimal throttle (default: 10.0)")

    args = parser.parse_args()    
    
    manualCalibration(args.motorId, args.minThrottle)
    
