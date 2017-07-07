'''
Created on 6 jul. 2017

@author: david
'''
from time import sleep

from device.manager import JoystickManager


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
            
            
    def start(self):
        '''
        Starts controller activity
        '''
        
        if self._joystick and not self._started:
            
            self._started = True
            
            while self._started:
                sleep(0.2)
    
        
    def stop(self):
        '''
        Stops controller activity
        '''
        
        self._started = False        
        self._joystickManager.stop()
        
    
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
                print("Direction: {0}".format(axisValue))
            elif index == 4:
                #Throttle
                print("Throttle: {0}".format(axisValue))
        
    

    def _onJoystickButtonPressed(self, sender, index):
        '''
        Process button pressed event from joystick
        @param sender: Joystick object who raised the event
        @param index: Index of button
        '''
        
        if sender == self._joystick:
            
            print("Button: {0}".format(index))
            
            if index == 0:
                self._started = False
    