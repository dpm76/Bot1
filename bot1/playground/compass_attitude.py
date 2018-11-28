'''
Created on 26 nov. 2018

@author: david
'''
import logging
import time
from sensor.attitude import AttitudeSensor

logging.basicConfig(level=logging.DEBUG)

print("Press CTRL+C to finish")

sensor = AttitudeSensor(channel=1)
sensor.start()
try:
    
    calibTime = 30
    logging.info("Starting magnetometer calibration: move device for {0}s".format(calibTime))
    sensor.calibrate(calibTime)
    logging.info("Magnetometer calibration finished")
    
    while True:
        
        heading = sensor.readAngleZ()
        logging.info("Heading = {0:.3f}°".format(heading))
        time.sleep(0.1)

except KeyboardInterrupt:
    
    print("CTRL+C pressed. Finishing...")

finally:

    sensor.stop()
    print("Bye!")

