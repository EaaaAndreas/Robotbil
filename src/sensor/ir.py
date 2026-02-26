from machine import Pin, ADC
import time

sensor = ADC(26)   # <-- Correct class name

def ir():
        value = sensor.read_u16()   # more accurate than .value()
        print(sensor.read_u16())
        if value > 40000: #skidt 
            #black line
            result = True
        else:
            #white line
            result = False
        
        return result

if __name__ == '__main__':
    while True:
        ir()