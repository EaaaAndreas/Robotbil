from machine import Pin, PWM
from time import sleep

class MotorController:
    def __init__(self):
        # Motor A pins
        self.ena = PWM(Pin(0))
        self.in1 = Pin(1, Pin.OUT)
        self.in2 = Pin(2, Pin.OUT)
        # Motor B pins
        self.enb = PWM(Pin(5))
        self.in3 = Pin(3, Pin.OUT)
        self.in4 = Pin(4, Pin.OUT)
        # Set PWM frequency
        self.ena.freq(1000)
        self.enb.freq(1000)

    def motorA_forward(self, speed=50000):
        self.in1.high()
        self.in2.low()
        self.ena.duty_u16(speed)

    def motorA_backward(self, speed=50000):
        self.in1.low()
        self.in2.high()
        self.ena.duty_u16(speed)

    def motorA_stop(self):
        self.in1.low()
        self.in2.low()
        self.ena.duty_u16(0)

    def motorB_forward(self, speed=50000):
        self.in3.high()
        self.in4.low()
        self.enb.duty_u16(speed)

    def motorB_backward(self, speed=50000):
        self.in3.low()
        self.in4.high()
        self.enb.duty_u16(speed)

    def motorB_stop(self):
        self.in3.low()
        self.in4.low()
        self.enb.duty_u16(0)

if __name__ == "__main__":
    motors = MotorController()
    while True:
        motors.motorA_forward(2**15)
        motors.motorB_forward(2**15)
        sleep(2)

        motors.motorA_backward(2**16)
        motors.motorB_backward(2**16)
        sleep(2)

        motors.motorA_stop()
        motors.motorB_stop()
        sleep(1)
        break
