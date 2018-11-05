'''
Created on 2 nov. 2018

@author: david
'''
import select

from threading import Thread

from engine.sysfs_writer import SysfsWriter


class WheelMotion(object):
    '''
    Wheel motion sensor
    '''
    
    POLL_TIMEOUT = 200

    def __init__(self, gpioPort):
        '''
        Constructor
        
        @param gpioPort: GPIO port where the sensor is attached to.
        '''
        
        self._gpioPort = gpioPort
        self._metersPerStep = 0.0
        self._isRunning = False
        self._pollThread = None
        
        self._stepCount = 0
        
        SysfsWriter.writeOnce("in", "/sys/class/gpio/gpio{0}/direction".format(self._gpioId))
        
    
    def start(self):
        '''
        Starts polling
        '''
        
        if self._pollThread == None or not self._pollThread.isAlive():
            self._stepCount = 0
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
        
        @return Number of steps.
        '''
        
        return self._stepCount
    
    
    def getTravelDistance(self):
        '''
        Gets distance travelled since the sensor was started.
        
        @return Number of steps.
        '''
        
        return self._stepCount * self._metersPerStep
    
    
    def _doPoll(self):
        '''
        Performs the polling thread
        '''
        
        sysfile = open("/sys/class/gpio/gpio{0}/value".format(self._gpioPort), "r")
        pollingObj = select.poll()
        sysfile.readline()
        pollingObj.register(sysfile, select.POLLPRI | select.POLLERR)
        
        try:
            while self._isRunning:
        
                _, event = pollingObj.poll(WheelMotion.POLL_TIMEOUT)
                if event == select.POLLPRI:
                    sysfile.seek(0)
                    if sysfile.readline()[0] == '0':
                        self._stepCount += 1
        
        finally:
        
            pollingObj.unregister(sysfile)
            sysfile.close()

    