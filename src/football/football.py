# src/football/football.py
from motor import *
import ustruct
ACTIVE = False


__all__ = ["start_football", "stop_football", "fb_control"]


def slight_left(power):
    left_motor.set_speed(power/2)
    right_motor.set_speed(power)

def slight_right(power):
    left_motor.set_speed(power)
    right_motor.set_speed(power/2)

def drive_r(power):
    drive(-power)

def right_r(power):
    slight_right(-power)

def left_r(power):
    slight_left(-power)

def stp(*_):
    stop()

_drive = {
    b'NN': drive,
    b'WW': turn_hard_left,
    b'EE': turn_hard_right,
    b'SS': drive_r,
    b'NW': slight_left,
    b'NE': slight_right,
    b'SW': left_r,
    b'SE': right_r,
    b'XX': stp,
}


def start_football():
    global ACTIVE
    ACTIVE = True

def stop_football():
    global ACTIVE
    ACTIVE = False

def fb_control(cmd:bytes):
    if ACTIVE:
        print("[Football]", cmd)
        cmd, pwr = ustruct.unpack('2sB', cmd)
        _drive[cmd](pwr)
    else:
        stop()
        cmd, pwr = b'XX', 0
    return cmd, pwr, int(ACTIVE)