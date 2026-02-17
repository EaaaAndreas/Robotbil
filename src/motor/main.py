from machine import Pin, PWM
from time import sleep

class DCMotor:
    def __init__(self, pin_forward, pin_backward, pin_enable, freq=1000):
        self.forward = PWM(Pin(pin_forward, Pin.OUT))
        self.backward = PWM(Pin(pin_backward, Pin.OUT))
        self.enable = PWM(Pin(pin_enable, Pin.OUT))

        self.forward.freq(freq)
        self.backward.freq(freq)
        self.enable.freq(freq)

        self.stop()

        #Enables the motor(turning on the power)
        self.enable.duty_u16(65535)




    def set_speed(self, speed):
        """
        speed: -100 to 100
        positive = forward
        negative = backward
        """
        speed = max(-100, min(100, speed))
        duty = int(abs(speed) * 65535 / 100)

        if speed > 0:
            self.backward.duty_u16(0)
            self.forward.duty_u16(duty)
        elif speed < 0:
            self.forward.duty_u16(0)
            self.backward.duty_u16(duty)
        else:
            self.stop()

    def stop(self):
        self.forward.duty_u16(0)
        self.backward.duty_u16(0)

left_motor = DCMotor(3, 4, 5)
right_motor = DCMotor(1, 2, 0)

def main():
    left_motor.set_speed(40)
    right_motor.set_speed(-50)
    sleep(2)
    left_motor.stop()
    right_motor.stop()
    sleep(0.1)
    left_motor.set_speed(-40)
    right_motor.set_speed(50)
    sleep(2)
    left_motor.stop()
    right_motor.stop()


main()