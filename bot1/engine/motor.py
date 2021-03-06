# -*- coding: utf-8 -*-

"""
Created on 06/04/2015

@author: david
"""
import logging
from os import system
from os.path import exists

from engine.sysfs_writer import SysfsWriter
from sensor.wheel import WheelMotion 
from stabilization.pid import Pid


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
    
    DEFAULT_MIN_DUTY = PERIOD * 10 / 100 #nanoseconds
    NEUTRAL_DUTY = 0 #nanoseconds
    MAX_DUTY = PERIOD * 90 / 100 #nanoseconds Max duty cannot be more than 90% of the period.

    MAX_THROTTLE = 90.0 #percentage


    def __init__(self, motorId):
        """
        Constructor
        
        @param motorId: Identificator of the motor. Values are 0 or 1  
        """
        
        pinIndex = motorId
        self._pwmId = Motor._pins[pinIndex][Motor.KEY_PWM_ID]
        self._pinId = Motor._pins[pinIndex][Motor.KEY_PIN_ID]
        
        self._motorId = motorId
        
        self._minDuty = Motor.DEFAULT_MIN_DUTY
        self._updateRangeDuty()
        
        self._throttle = 0.0
        self._duty = Motor.NEUTRAL_DUTY

        self._gpioId = Motor._gpios[motorId]
    
    
    def _updateRangeDuty(self):
        
        self._rangeDuty = (Motor.MAX_DUTY - self._minDuty) / 100.0
           
           
    def resetMinThrottle(self):
        """
        Set current duty as minimal throttle 
        """
        
        self._minDuty = self._duty
        self._trottle = 0.0
        self._updateRangeDuty()
        
    
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
        #TODO: 20181114 DPM: This is not required to do if the throttle sign was not changed
        if self._throttle >= 0.0:
            SysfsWriter.writeOnce("0", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))
        else:
            SysfsWriter.writeOnce("1", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))
            

        #Throttle
        if absThrottle > 0.0 and absThrottle <= Motor.MAX_THROTTLE:            
        
            self._duty = int((self._rangeDuty * absThrottle) + self._minDuty)
        
        elif absThrottle == 0.0:
            self._setNeutralThrottle()
            
        else: # absThrottle > Motor.MAX_THROTTLE
            self._duty = int((self._rangeDuty * Motor.MAX_THROTTLE) + self._minDuty)
            self._throttle = Motor.MAX_THROTTLE if self._throttle > 0.0 else -Motor.MAX_THROTTLE

        self._sysfsWriter.write(str(self._duty))
        
    
    def getThrottle(self):
        
        return self._throttle
    
    
    def addThrottle(self, increment):
        """
        Increases or decreases the motor's throttle
        
        @param increment: Value added to the current throttle percentage. This can be negative to decrease.
        """
        
        self.setThrottle(self._throttle + increment)

        
    def _setNeutralThrottle(self):
        """
        Set the motor at neutral
        """
        
        self._throttle = 0.0
        self._duty = Motor.NEUTRAL_DUTY        
        self._sysfsWriter.write(str(self._duty))
        SysfsWriter.writeOnce("0", "/sys/class/gpio/gpio{0}/value".format(self._gpioId))       
        
    
    def setNeutralThrottle(self):
        """
        Set the motor at neutral
        """
        
        self._setNeutralThrottle()
        
        
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
        
        
    def _log(self, message):
        """
        Logs a message
        @param message: Message to log
        """
        
        msg = "motor {0}: {1}".format(self._motorId, message)
        logging.debug(msg)
        #print(msg)
        
    
    def start(self):
        """
        Starts the motor up
        """
        
        self.setNeutralThrottle()
        
        self._log("started")
        
        
    def setThrottle(self, throttle):
        """
        Sets the motor's throttle
        
        @param throttle: Motor power as percentage 
        """
        
        self._throttle = float(throttle)        
        absThrottle = abs(self._throttle)
            
        if absThrottle > Motor.MAX_THROTTLE:            
            self._throttle = Motor.MAX_THROTTLE if self._throttle >= 0.0 else -Motor.MAX_THROTTLE

        self._log("throttle: {0}".format(self._throttle))
                
    
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
        
        self._log("throttle: {0}".format(self._throttle))
        
        
    def stop(self):
        """
        Stops the motor
        """
        
        self._log("stop")

        self.setNeutralThrottle()        
        

class StepMotor(Motor):
    
    PID_PERIOD = 0.05
    STEP_SPEED_MAX = 30.0 # steps/s
    
    KP = 0.5
    KI = 2.5
    KD = 0.05
    
    _stepGpios = [69, 68] #TODO: 20181112 DPM: GPIO port for motor #1 
    
    def __init__(self, motorId):
        
        super().__init__(motorId)
        #TODO: 20181112 DPM: The sensor could be get from a pool. The pilot uses the same sensor too.
        self._wheelSensor = WheelMotion(StepMotor._stepGpios[motorId])
        self._pid = Pid(StepMotor.PID_PERIOD, 1, self._readSensorInput, self._setPidOutput, "PID_{0}#{1}".format(type(self).__name__, motorId))\
            .setProportionalConstants([StepMotor.KP])\
            .setIntegralConstants([StepMotor.KI])\
            .setDerivativeConstants([StepMotor.KD])
        
        self._stepSpeedTarget = 0.0

    
    def _readSensorInput(self):
            
        sensorInput = [-self._wheelSensor.getCurrentStepSpeed()\
                       if self._stepSpeedTarget < 0.0\
                       else self._wheelSensor.getCurrentStepSpeed()]
        
        logging.debug("Wheel sensor input: {0:.3f}".format(sensorInput[0]))
        
        return sensorInput
    
    
    def _setPidOutput(self, output):
        
        logging.debug("wheel output: {0:.3f}".format(output[0]))
        super().setThrottle(output[0])
    
    
    def getWheelMotionSensor(self):
        
        return self._wheelSensor
    
    
    def start(self):
        
        self._wheelSensor.start()
        super().start()
        self._pid.start()
    
    
    def stop(self):
    
        self._pid.stop()
        super().stop()
        self._wheelSensor.stop()
        
                
    def setNeutralThrottle(self):
        
        self.setThrottle(0.0)            
        super().setNeutralThrottle()
        
        
    def setThrottle(self, throttle):
        
        if throttle != 0.0:
            
            if (self._stepSpeedTarget < 0.0 and throttle > 0.0) or\
                (self._stepSpeedTarget > 0.0 and throttle < 0.0):
                self._pid.resetIntegrals()
            
            self._stepSpeedTarget = throttle * StepMotor.STEP_SPEED_MAX / 100.0
            self._pid.setTargets([self._stepSpeedTarget])
            
            if self._pid.isPaused():
                
                self._pid.resetIntegrals()
                self._pid.resume()
            
        else:

            self._pid.pause()
            