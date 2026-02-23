from machine import Pin, PWM
from time import sleep


class DCMotor:
    def __init__(self, pin_forward, pin_backward, pin_enable, trim=1.0, freq=1000):
        # Initialiser pins
        #FIXME PWM andre steder end enable er ik nødvendigt(kan vente med det til sidst)
        self.forward = PWM(Pin(pin_forward, Pin.OUT))
        self.backward = PWM(Pin(pin_backward, Pin.OUT))
        self.enable = PWM(Pin(pin_enable, Pin.OUT))


        self.forward.freq(freq)
        self.backward.freq(freq)
        self.enable.freq(freq)

        # Trim skal sættes FØR stop
        self.trim = trim

        # FIXME: Det er netop den trim vi skal have gjort dynamisk (afhængig af farten). Så den skal klares på en anden måde.

        # Tænd motoren
        self.enable.duty_u16(65535)

        # For at kunne stoppe en valgfri motor vi har registreret motoren
        self.stop()

    def set_speed(self, speed):
        speed = max(-100, min(100, speed))
        duty = int(abs(speed) * 65535 / 100 * self.trim)



        # FIXME: Bruger vi mere processing power på at løse 65535 / 100 selv, eller ved at sætte pigen til at gøre det 200 gange/sekund?

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

def turn_hard_left(power): #dreje venstre på stedet
    left_motor.set_speed(-power)
    right_motor.set_speed(power)

def turn_hard_right(power): #dreje højre på stedet
    left_motor.set_speed(power)
    right_motor.set_speed(-power)

def stop():
    left_motor.stop()
    right_motor.stop()

def turn_right(power):
    left_motor.set_speed(power)
    right_motor.set_speed(power-30)
    sleep(0.5)

def turn_left(power):
    left_motor.set_speed(power-30)
    right_motor.set_speed(power)
    sleep(0.5)

def drive(power):
    left_motor.set_speed(power)
    right_motor.set_speed(power)

# Opret motorer med ;pin_forward, pin_backwards, pin_enable, trim(styke %)
left_motor = DCMotor(3, 4, 5, trim=0.75)
right_motor = DCMotor(1, 2, 0, trim=1.0)

