# -*- coding: utf-8 -*-
'''
Created on 23 oct. 2018

@author: david
'''

class ImuDummy(object):
    '''
    Emulates a IMU/MPU sensor.
    Intended for testing.
    '''
    
    def __init__(self, fixedAngSpeeds):
        '''
        Constructor
        
        @param fixedAngSpeeds: Array with the angle speed values 
        '''
        
        self._fixedAngSpeeds = fixedAngSpeeds
        
    
    def start(self):
        '''
        Inits the sensor.
        '''
        
        pass
    
    
    def stop(self):
        '''
        Stops the sensor
        '''
        
        pass
    
    
    def readAngSpeedZ(self):
        '''
        Reads a emulated angular speed.
        
        returns: Angular speed as degrees/second
        '''
        
        return self._fixedAngSpeeds[2]
    