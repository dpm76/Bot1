'''
Created on 6 jul. 2017

@author: david
'''
import rpyc
from time import sleep

from device.manager import JoystickManager
from engine.driver import Driver


class Controller(object):
    '''
    Remote controller
    '''
    
    #Driving modes map. The value of each entry indicates the next mode when the key is the current mode.
    _modeMap = { Driver.MODE_NORMAL : Driver.MODE_ROTATE, 
                Driver.MODE_ROTATE : Driver.MODE_NORMAL }

    def __init__(self):
        '''
        Constructor
        '''
        
        self._started = False
        
        self._connection = None
        self._driver = None
        
        self._joystickManager = JoystickManager.getInstance()
        self._joystickManager.start()
        joysticks = self._joystickManager.getJoysticks()        
        
        if len(joysticks) != 0:
            self._joystick = joysticks[0]
            self._joystick.onAxisChanged += self._onJoystickAxisChanged
            self._joystick.onButtonPressed += self._onJoystickButtonPressed
        else:
            self._joystick = None            
            
            
    def start(self, remoteAddress=None, testing=False, local=False):
        '''
        Starts controller activity
        
        @param remoteAddress: Robot's network address
        @param testing: Boolean value indicating whether it should run in testing context
        @param local: If true runs on local machine instead of remotely 
        '''
        
        if not self._joystick:
            raise Exception("No joystick available!")
        
        if self._joystick and not self._started:
            
            if not local:
                self._connection = rpyc.classic.connect(remoteAddress)
                self._driver = self._connection.modules["engine.driver"].Driver.createForTesting() \
                                if testing else \
                                self._connection.modules["engine.driver"].Driver.createForRobot()
            else: #Running localy
                self._driver = Driver.createForTesting() \
                                if testing else \
                                Driver.createForRobot()
            
            self._driver.start()            
            self._started = True
            
            while self._started:
                sleep(0.2)
    
        
    def stop(self):
        '''
        Stops controller activity
        '''
                
        self._joystickManager.stop()
        if self._driver:
            self._driver.stop()
        
        if self._connection:
            self._connection.close()
        
        self._started = False
        
    
    def _onJoystickAxisChanged(self, sender, index):
        '''
        Process axis changed event from joystick
        @param sender: Joystick object who raised the event
        @param index: Index of axis
        '''
        
        if sender == self._joystick:
            axisValue = sender.getAxisValue(index)
            
            if index == 3: #Usually the horizontal axis of the left stick
                #Direction
                if self._driver.getMode() == Driver.MODE_NORMAL:
                    self._driver.setDirection(-axisValue * 2.0)
                else:
                    self._driver.setDirection(axisValue / 2.0)
                
                
            elif index == 4: #Usually the vertical axis of the left stick
                #Throttle
                
                #The axis value is inverted as should be intuitive: 
                #    negative values are fordwards
                #    positive values are backwards
                # Therefore the passed value is negated.
                self._driver.setThrottle(axisValue / 2.0)
    

    def _onJoystickButtonPressed(self, sender, index):
        '''
        Process button pressed event from joystick
        @param sender: Joystick object who raised the event
        @param index: Index of button
        '''
        
        if sender == self._joystick:
            
            if index == 0: #Usually A-button
                
                self._started = False
                
            elif index == 1: #Usually B-button
                
                currentDrivingMode = self._driver.getMode()
                nextDrivingMode = Controller._modeMap[currentDrivingMode]
                self._driver.setMode(nextDrivingMode)
                
    