# -*- coding: utf-8 -*-

'''
Created on 06/04/2015

@author: david
'''
from os import system


class SysfsWriter(object):
    
    @staticmethod
    def writeOnce(text, path):
        '''
        writer = SysfsWriter(path)
        writer.write(text)
        writer.close()
        '''
        system("echo {0} > {1}".format(text, path))

    def __init__(self, path):
        '''
        Constructor
        '''
        
        self._file = open(path, "a")
        
        
    def write(self, text):
        
        self._file.write(text)
        self._file.flush()
        
        
    def close(self):
        
        self._file.close()
        
