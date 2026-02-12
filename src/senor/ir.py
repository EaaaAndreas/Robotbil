from machine import Pin, ADC
import time

sensor = ADC(Pin(26))   # <-- Correct class name

def ir():
        value = sensor.read_u16()   # more accurate than .value()
        print("Raw:", value)

        if value < 20000:
            print("BLACK LINE")
        else:
            print("WHITE SURFACE")

        print()
        time.sleep(0.1)

if __name__ == '__main__':
    while True:
        ir()