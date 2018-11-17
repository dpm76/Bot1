from os.path import exists

class Pwm(object):
    '''
    Encapsulates the PWM-signal generator.
    It uses the sysfs to work
    '''
    
    def __init__(self, port):
        '''
        Constructor
        
        @param port: PWM Port number. It depends on the concrete machine where the programm will run.
        '''
        
        self._port = port
        
        #Enable port if it isn't already done
        if not exists("/sys/class/pwm/pwm{0}".format(self._port)):
            f = open("/sys/class/pwm/export", "w")
            f.write(str(self._port))
            f.flush()
            f.close()
            
        #Reset values
        self.stop()
        self.setDuty(0)        
        
    
    def setPeriod(self, period):
        '''
        Set the period value. This is the period between pulses.
        
        @param period: nanoseconds
        '''
        
        f = open("/sys/class/pwm/pwm{0}/period_ns".format(self._port), "w")
        f.write(str(int(period)))
        f.flush()
        f.close()
        
        self._period = period
        
        
    def setFreq(self, freq):
        '''
        Set the frequency at pulses are generated
        
        @param freq: Frequency as Hertz
        '''
        
        period = 1000000000.0/freq        
        self.setPeriod(period)
        
        
    def setDuty(self, duty):
        '''
        Set the duty value. This is the time the signal is high within the pulse.
        
        @param duty: nanoseconds
        '''
        
        f = open("/sys/class/pwm/pwm{0}/duty_ns".format(self._port), "w")
        f.write(str(int(duty)))
        f.flush()
        f.close()
        
        self._duty = duty
        
        
    def setDutyPerc(self, perc):
        '''
        Set the duty value as a percentage according to the period of the pulse.
        
        @param perc: Percentage value between 0 and 100
        '''
        
        duty = self._period * float(perc) / 100.0
        self.setDuty(duty)
        
        
    def start(self):
        '''
        Starts the PWM-signal generation
        '''
        
        f = open("/sys/class/pwm/pwm{0}/run".format(self._port), "w")
        f.write("1")
        f.flush()
        f.close()        
        
        
    def stop(self):
        '''
        Stops the PWM-signal generation
        '''
        
        self.setDuty(0)
        
        f = open("/sys/class/pwm/pwm{0}/run".format(self._port), "w")
        f.write("0")
        f.flush()
        f.close()        

        
        
    def cleanup(self):
        '''
        Frees all using resources
        '''
        
        f = open("/sys/class/pwm/unexport", "w")
        f.write(str(self._port))
        f.flush()
        f.close()
        