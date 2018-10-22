'''
Created on 8 oct. 2018

@author: david
'''
import logging

from state.event import EventHook
from threading import Thread


class CollisionDetector(object):
    
    def __init__(self, accelProvider, threshold):
        
        self._accelProvider = accelProvider
        self._threshold = threshold
        
        self.onCollision = EventHook()
        
        self._isRunning = False
        self._thread = None
        
        
    def start(self):
        
        if self._thread == None or not self._thread.isAlive():
            
            logging.info("Starting collision detector")
            
            self._isRunning = True
            self._thread = Thread(target=self._do)
            self._thread.start()
    
    
    def stop(self):
        
        self._isRunning = False
        if self._thread != None and self._thread.isAlive():
            
            self._thread.join()
            
            logging.info("Collision detector stopped")
        
        
    def _do(self):
        
        while self._isRunning:
            
            #TODO: 20181008 DPM: Floor's plane change and wanted acceleration 
            #    or decceleration are not taking into account currently.
            accelY = self._accelProvider.readAccelY()
            if abs(accelY) > self._threshold:
                self.onCollision.fire()
               
    