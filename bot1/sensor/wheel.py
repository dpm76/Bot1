'''
Created on 2 nov. 2018

@author: david
'''
import select
from threading import Thread
import time

from engine.sysfs_writer import SysfsWriter
from state.event import EventHook


class WheelMotion(object):
    '''
    Wheel motion sensor
    '''
    
    POLL_TIMEOUT = 1000

    def __init__(self, gpioPort):
        '''
        Constructor
        
        @param gpioPort: GPIO port where the sensor is attached to.
        '''
        
        self.onStep = EventHook()
        
        self._gpioPort = gpioPort
        self._metersPerStep = 0.0
        self._isRunning = False
        self._pollThread = None        
        
        self._stepCount = 0
        self._stepTime = -1 
        
        SysfsWriter.writeOnce("in", "/sys/class/gpio/gpio{0}/direction".format(self._gpioPort))
        SysfsWriter.writeOnce("rising", "/sys/class/gpio/gpio{0}/edge".format(self._gpioPort))
        
    
    def start(self):
        '''
        Starts polling
        '''
        
        if self._pollThread == None or not self._pollThread.isAlive():
            self._stepCount = 0
            self._stepTime = -1            
            self._isRunning = True
            self._pollThread = Thread(target=self._doPoll)
            self._pollThread.start()
    
    
    def stop(self):
        '''
        Stops polling
        '''
        
        self._isRunning = False        
        if self._pollThread != None and self._pollThread.isAlive():
            
            self._pollThread.join()
    
    
    def resetStepCounter(self):
        '''
        Sets the step counter to zero
        '''
        
        self._stepCount = 0
        
        
    def notifyStoppedMotor(self):
        '''
        Tells the sensor the motor is stopped
        '''
        
        self._stepTime = -1        
    
    
    def setMetersPerStep(self, metersPerStep):
        '''
        Sets the distance travelled along one step, i.e. between two wheel holes.
        
        @param metersPerStep: Distance as meters
        '''
        
        self._metersPerStep = metersPerStep
        
        return self
    
    
    def getTravelSteps(self):
        '''
        Gets the number of steps since the sensor was started.
        
        @return: Number of steps.
        '''
        
        return self._stepCount
    
    
    def getTravelDistance(self):
        '''
        Gets distance travelled since the sensor was started.
        
        @return: Number of steps.        
        '''
        
        return self._stepCount * self._metersPerStep
    
    
    def getCurrentStepSpeed(self):
        '''
        Current step speed
        
        @return: steps/s 
        '''
        
        return (1.0 / self._stepTime)\
            if self._stepTime > 0.0\
            else 0.0
            
        
    
    def getCurrentSpeed(self):
        '''
        Current wheel speed.
        The distance between steps must be set before. 
        
        @see: setMetersPerStep
        @return: m/s
        '''
        
        return (self._metersPerStep / self._stepTime)\
            if self._stepTime > 0.0\
            else 0.0
    
    
    def _doPoll(self):
        '''
        Performs the polling thread
        '''
        
        sysfile = open("/sys/class/gpio/gpio{0}/value".format(self._gpioPort), "r")
        pollingObj = select.poll()
        sysfile.readline()
        pollingObj.register(sysfile, select.POLLPRI | select.POLLERR)
        
        try:
            lastStepTime = time.time()
            while self._isRunning:
        
                eventList = pollingObj.poll(WheelMotion.POLL_TIMEOUT)
                if len(eventList) != 0:
                    sysfile.seek(0)
                    if sysfile.readline()[0] == '0':
                        currentStepTime = time.time() 
                        self._stepTime = currentStepTime - lastStepTime
                        lastStepTime = currentStepTime
                        self._stepCount += 1
                        self.onStep.fire()
        
        finally:
        
            pollingObj.unregister(sysfile)
            sysfile.close()

    