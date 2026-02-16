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
        # Default speeds for each motor
        self.motorA_speed = 50000
        self.motorB_speed = 50000

    def set_motorA_speed(self, speed):
        self.motorA_speed = speed

    def set_motorB_speed(self, speed):
        self.motorB_speed = speed

    def motorA_forward(self, speed=None):
        if speed is None:
            speed = self.motorA_speed
        self.in1.high()
        self.in2.low()
        self.ena.duty_u16(speed)

    def motorA_backward(self, speed=None):
        if speed is None:
            speed = self.motorA_speed
        self.in1.low()
        self.in2.high()
        self.ena.duty_u16(speed)

    def motorA_stop(self):
        self.in1.low()
        self.in2.low()
        self.ena.duty_u16(0)

    def motorB_forward(self, speed=None):
        if speed is None:
            speed = self.motorB_speed
        self.in3.high()
        self.in4.low()
        self.enb.duty_u16(speed)

    def motorB_backward(self, speed=None):
        if speed is None:
            speed = self.motorB_speed
        self.in3.low()
        self.in4.high()
        self.enb.duty_u16(speed)

    def motorB_stop(self):
        self.in3.low()
        self.in4.low()
        self.enb.duty_u16(0)

    def turn_left(self, speedA=None, speedB=None):
        # Motor A backward, Motor B forward
        self.motorA_forward(speedA)
        self.motorB_forward(speedB)

    def turn_right(self, speedA=None, speedB=None):
        # Motor A forward, Motor B backward
        self.motorA_forward(speedA)
        self.motorB_forward(speedB)

if __name__ == "__main__":
    motors = MotorController()
    # Example: Set different speeds for each motor
    motors.set_motorA_speed(40000)  # slower
    motors.set_motorB_speed(60000)  # faster
    while True:
        motors.motorA_forward()  # uses set speed
        motors.motorB_forward()  # uses set speed
        sleep(2)

        motors.turn_left() #set Amoter forword, set Bmoter forword 
        sleep(1)

        motors.turn_right() #set Amoter forword, set Bmoter forword
        sleep(1)

        motors.motorA_backward()
        motors.motorB_backward()
        sleep(2)

        motors.motorA_stop()
        motors.motorB_stop()
        sleep(1)
        break