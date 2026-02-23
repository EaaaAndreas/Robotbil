# src/football/football.py
from motor import *


ACTIVE = False

__all__ = ["start_football", "stop_football", "fb_callbacks"]

def start_football():
    global ACTIVE
    ACTIVE = True

def stop_football():
    global ACTIVE
    ACTIVE = False

def forward():
    pass

def backward():
    pass

def right():
    pass

def left():
    pass

def stop():
    pass

fb_callbacks = [
    forward,
    backward,
    right,
    left,
    stop,
]

if __name__ == "__main__":
    pass
