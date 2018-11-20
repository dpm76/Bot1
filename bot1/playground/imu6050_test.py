from sensor.imu6050 import Imu6050
import time

print("Press CTRL+C to stop")
imu = Imu6050()

imu.start()
try:
    imu.updateGyroTime()
    while True:
        print("{0:.3f}°".format(imu.readAngleZ()))
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nBye!")
finally:
    imu.stop()
    