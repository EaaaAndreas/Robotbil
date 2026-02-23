import time
from machine import Pin

time.sleep_ms(5)
gy53 = Pin(17, Pin.IN) # Initialize GY-53 I2C pin

def tof():
    time.sleep_ms(10)  # Wait for sensor to power up (adjust as needed)

    while gy53.value() == 1: # Wait for the GY-53 to become ready
        pass
    while gy53.value() == 0: # Wait for the pulse to go high
        pass
    starttime = time.ticks_us()
    while gy53.value() == 1: # Wait for the pulse to go low
        pass
    endtime = time.ticks_us()



    distance = time.ticks_diff(endtime , starttime) / 100 * 10
    print(distance, "mm") #print our data
    #time.sleep(1) #skift til 0.1 hvis den skal printe ud data hurtigere
    return distance

if __name__ == '__main__':
    while True:
        tof()