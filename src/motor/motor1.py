from machine import Pin, PWM
from time import sleep

# Motor A pins
ena = PWM(Pin(0))
in1 = Pin(1, Pin.OUT)
in2 = Pin(2, Pin.OUT)

# Motor B pins
enb = PWM(Pin(5))
in3 = Pin(3, Pin.OUT)
in4 = Pin(4, Pin.OUT)

# Set PWM frequency
ena.freq(1000)
enb.freq(1000)

def motorA_forward(speed=50000):
    in1.high()
    in2.low()
    ena.duty_u16(speed)

def motorA_backward(speed=50000):
    in1.low()
    in2.high()
    ena.duty_u16(speed)

def motorA_stop():
    in1.low()
    in2.low()
    ena.duty_u16(0)

def motorB_forward(speed=50000):
    in3.high()
    in4.low()
    enb.duty_u16(speed)

def motorB_backward(speed=50000):
    in3.low()
    in4.high()
    enb.duty_u16(speed)

def motorB_stop():
    in3.low()
    in4.low()
    enb.duty_u16(0)

if __name__ == '__main__':
    # Demo loop
    while True:
        motorA_forward(2**16)
        motorB_forward(2**16)
        sleep(2)

        motorA_backward(2**16)
        motorB_backward(2**16)
        sleep(2)

        motorA_stop()
        motorB_stop()
        sleep(1)