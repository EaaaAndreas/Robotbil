from machine import Pin
import time

ir = Pin(27, Pin.IN, Pin.PULL_DOWN)

while True:
    if ir.value() == 1:
        print("1")
    else:
        print("0")

    time.sleep(0.2)