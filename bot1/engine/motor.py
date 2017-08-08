# -*- coding: utf-8 -*-

"""
Created on 06/04/2015

@author: david
"""
import logging
from os import system
from os.path import exists

from engine.sysfs_writer import SysfsWriter


class Motor(object):
    """
    Controls a single motor
    """
    
    KEY_PWM_ID = "pwmId"
    KEY_PIN_ID = "pinId" 
    
    #BeagleBone's config.
    #TODO 20150408 DPM - Include this configuration in such a settings file
    _pins = [{KEY_PWM_ID: 6, KEY_PIN_ID: "P8.13"},
             {KEY_PWM_ID: 5, KEY_PIN_ID: "P8.19"}]
    #{KEY_PWM_ID: 4, KEY_PIN_ID: "P9.16"},
    #{KEY_PWM_ID: 3, KEY_PIN_ID: "P9.14"}]
    _gpios = ["27", "26"]
    
    PERIOD = 20000000 #nanoseconds = 50Hz
    
    MIN_DUTY = PERIOD * 30 / 100 #nanoseconds
    NEUTRAL_DUTY = 0 #nanoseconds
    MAX_DUTY = PERIOD * 90 / 100 #nanoseconds Max duty cannot be more than 90% of the period.
    
    RANGE_DUTY = (MAX_DUTY - MIN_DUTY) / 100.0

    MAX_THROTTLE = 100.0 #percentage


    def __init__(self, motorId):
        """
        Constructor
        
        @param motorId: Identificator of the motor. A number between 0 to 3 (in case of quadcopter)  
        """
        
        pinIndex = motorId
        self._pwmId = Motor._pins[pinIndex][Motor.KEY_PWM_ID]
        self._pinId = Motor._pins[pinIndex][Motor.KEY_PIN_ID]
        
        self._motorId = motorId
        
        self._throttle = 0.0
        self._duty = Motor.NEUTRAL_DUTY

        self._gpioId = Motor._gpios[motorId]
        
    
    def start(self):
        """
        Starts the motor up
        """
        
        if not exists("/sys/class/pwm/pwm{0}".format(self._pwmId)):
            system("config-pin {0} pwm".format(self._pinId))
            #SysfsWriter.writeOnce("pwm", "/sys/devices/ocp.*/{0}_pinmux.*/state".format(self._pinId))
            SysfsWriter.writeOnce(str(self._pwmId), "/sys/class/pwm/export")
        
        SysfsWriter.writeOnce("0", "/sys/class/pwm/pwm{0}/duty_ns".format(self._pwmId))
        SysfsWriter.writeOnce("0", "/sys/class/pwm/pwm{0}/run".format(self._pwmId))
        SysfsWriter.writeOnce(str(Motor.PERIOD), "/sys/class/pwm/pwm{0}/period_ns".format(self._pwmId))
        SysfsWriter.writeOnce("1", "/sys/class/pwm/pwm{0}/run".format(self._pwmId))
        
        SysfsWriter.writeOnce("out", "/sys/class/gpio/gpio{0}/direction".format(self._gpioId))
        SysfsWriter.writeOnce("0", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))

        self._sysfsWriter = SysfsWriter("/sys/class/pwm/pwm{0}/duty_ns".format(self._pwmId))

        self.setNeutralThrottle()
        
        logging.info("motor {0}: started".format(self._motorId))
        
        
    def setThrottle(self, throttle):
        """
        Sets the motor's throttle
        
        @param throttle: Motor power as percentage 
        """
        
        self._throttle = float(throttle)        
        absThrottle = abs(self._throttle)
        
        #Fordwards or backwards movement
        if self._throttle >= 0.0:
            SysfsWriter.writeOnce("0", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))
        else:
            SysfsWriter.writeOnce("1", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))
            

        #Throttle
        if absThrottle > 0.0 and absThrottle <= Motor.MAX_THROTTLE:            
        
            self._duty = int((Motor.RANGE_DUTY * absThrottle) + Motor.MIN_DUTY)
        
        elif absThrottle == 0.0:
            self._duty = Motor.NEUTRAL_DUTY
            
        else: # absThrottle > Motor.MAX_THROTTLE
            self._duty = Motor.MAX_DUTY
            self._throttle = Motor.MAX_THROTTLE if self._throttle >= 0.0 else -Motor.MAX_THROTTLE

        self._sysfsWriter.write(str(self._duty))
        
    
    def getThrottle(self):
        
        return self._throttle
    
    
    def addThrottle(self, increment):
        """
        Increases or decreases the motor's throttle
        
        @param increment: Value added to the current throttle percentage. This can be negative to decrease.
        """
        
        self.setThrottle(self._throttle + increment)
        
        
    def setNeutralThrottle(self):
        """
        Set the motor at neutral
        """
        
        self._throttle = 0.0
        self._duty = Motor.NEUTRAL_DUTY
        SysfsWriter.writeOnce("0", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))
        self._sysfsWriter.write(str(self._duty))       
        
        
    def stop(self):
        """
        Stops the motor
        """
        
        logging.info("motor {0}: stop".format(self._motorId))

        self.setNeutralThrottle()        
        
        self._sysfsWriter.close()
        SysfsWriter.writeOnce("0", "/sys/class/pwm/pwm{0}/run".format(self._pwmId))
        SysfsWriter.writeOnce("0", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))
        
    
class MotorDummy(object):
    """
    Controls a dummy motor
    """

    MAX_THROTTLE = 100.0 #percentage


    def __init__(self, motorId):
        """
        Constructor
        
        @param motorId: Identificator of the motor. A number between 0 to 3 (in case of quadcopter)  
        """
        
        self._motorId = motorId        
        self._throttle = 0.0
        
    
    def start(self):
        """
        Starts the motor up
        """
        
        self.setNeutralThrottle()
        
        msg = "motor {0}: started".format(self._motorId)
        logging.debug(msg)
        print(msg)
        
        
    def setThrottle(self, throttle):
        """
        Sets the motor's throttle
        
        @param throttle: Motor power as percentage 
        """
        
        self._throttle = float(throttle)        
        absThrottle = abs(self._throttle)
            
        if absThrottle > Motor.MAX_THROTTLE:            
            self._throttle = Motor.MAX_THROTTLE if self._throttle >= 0.0 else -Motor.MAX_THROTTLE

        msg="motor {0} throttle: {1}".format(self._motorId, self._throttle)
        logging.debug(msg)
        print(msg)
        
    
    def getThrottle(self):
        
        return self._throttle
    
    
    def addThrottle(self, increment):
        """
        Increases or decreases the motor's throttle
        
        @param increment: Value added to the current throttle percentage. This can be negative to decrease.
        """
        
        self.setThrottle(self._throttle + increment)
        
        
    def setNeutralThrottle(self):
        """
        Set the motor at neutral
        """
        
        self._throttle = 0.0
        msg="motor {0} throttle: {1}".format(self._motorId, self._throttle)
        logging.debug(msg)
        print(msg)       
        
        
    def stop(self):
        """
        Stops the motor
        """
        
        msg="motor {0}: stop".format(self._motorId)
        logging.debug(msg)
        print(msg)

        self.setNeutralThrottle()        
        
