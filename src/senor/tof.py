import time
from machine import Pin

time.sleep_ms(5)
gy53 = Pin(16, Pin.IN) # Initialize GY-53 I2C pin

def tof():
    time.sleep_ms(10)  # Wait for sensor to power up (adjust as needed)

    while gy53.value() == True: # Wait for the GY-53 to become ready
        pass
    while gy53.value() == False: # Wait for the pulse to go high
        pass
    starttime = time.ticks_us()
    while gy53.value() == True: # Wait for the pulse to go low
        pass
    endtime = time.ticks_us()



    distance = time.ticks_diff(endtime , starttime) / 100
    print(distance, "cm") #print our data
    time.sleep(1) #skift til 0.1 hvis den skal printe ud data hurtigere
    return distance

while True:
    tof()