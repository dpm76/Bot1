'''
Created on 6 jul. 2017

@author: david
'''
from time import sleep

from device.manager import JoystickManager

import rpyc


class Controller(object):
    '''
    Remote controller
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self._started = False
        
        self._joystickManager = JoystickManager.getInstance()
        self._joystickManager.start()
        joysticks = self._joystickManager.getJoysticks()        
        
        if len(joysticks) != 0:
            self._joystick = joysticks[0]
            self._joystick.onAxisChanged += self._onJoystickAxisChanged
            self._joystick.onButtonPressed += self._onJoystickButtonPressed
        else:
            self._joystick = None            
            
            
    def start(self, remoteAddress, testing=False):
        '''
        Starts controller activity
        @param remoteAddress: Robot's network address
        @param testing: Boolean value indicating wether it should run in testing context
        '''
        
        if self._joystick and not self._started:
            
            self._connection = rpyc.classic.connect(remoteAddress)
            self._driver = self._connection.modules["engine.driver"].Driver.createForTesting() \
                            if testing else \
                            self._connection.modules["engine.driver"].Driver.createForRobot()
            
            self._driver.start()            
            self._started = True
            
            while self._started:
                sleep(0.2)
    
        
    def stop(self):
        '''
        Stops controller activity
        '''
                
        self._joystickManager.stop()
        self._driver.stop()
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
            
            if index == 3:
                #Direction
                self._driver.setDirection(axisValue)
                
            elif index == 4:
                #Throttle
                self._driver.setThrottle(-axisValue)
                
                
            #throttle = self._driver.getThrottle()
            #direction = self._driver.getDirection()
            
            #print("({0},{1})".format(throttle, direction))
        
    

    def _onJoystickButtonPressed(self, sender, index):
        '''
        Process button pressed event from joystick
        @param sender: Joystick object who raised the event
        @param index: Index of button
        '''
        
        if sender == self._joystick:
            
            if index == 0:
                self._started = False
    