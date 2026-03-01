# src/football/football.py
from motor import *
import ustruct
ACTIVE = False


__all__ = ["start_football", "stop_football", "fb_control"]


def drive_r(power):
    drive(-power)

def right_r(power):
    turn_right(-power)

def left_r(power):
    turn_left(-power)

def stp(*_):
    stop()

_drive = {
    b'NN': drive,
    b'WW': turn_hard_left,
    b'EE': turn_hard_right,
    b'SS': drive_r,
    b'NW': turn_left,
    b'NE': turn_right,
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
        cmd, pwr = b'X', 0
    return cmd, pwr, int(ACTIVE)