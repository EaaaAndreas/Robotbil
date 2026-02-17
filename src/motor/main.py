from machine import Pin, PWM
from time import sleep


class DCMotor:
    def __init__(self, pin_forward, pin_backward, pin_enable, trim=1.0, freq=1000):
        # Initialiser pins
        self.forward = PWM(Pin(pin_forward, Pin.OUT))
        self.backward = PWM(Pin(pin_backward, Pin.OUT))
        self.enable = PWM(Pin(pin_enable, Pin.OUT))

        self.forward.freq(freq)
        self.backward.freq(freq)
        self.enable.freq(freq)

        # Trim skal sættes FØR stop
        self.trim = trim

        # Tænd motoren
        self.enable.duty_u16(65535)

        # Stop motoren
        self.stop()

    def set_speed(self, speed):
        speed = max(-100, min(100, speed))
        duty = int(abs(speed) * 65535 / 100 * self.trim)

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


# Opret motorer med ;pin_forward, pin_backwards, pin_enable, trim(styke %)
left_motor = DCMotor(3, 4, 5, trim=0.75)
right_motor = DCMotor(1, 2, 0, trim=1.0)


def main():
    # Frem
    left_motor.set_speed(50)
    right_motor.set_speed(50)
    sleep(2)

    left_motor.stop()
    right_motor.stop()
    sleep(1)

    # Bak
    left_motor.set_speed(-50)
    right_motor.set_speed(-50)
    sleep(2)

    left_motor.stop()
    right_motor.stop()


main()