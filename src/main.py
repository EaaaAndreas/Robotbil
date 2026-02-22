# /main.py
from connectivity.porting import *


PRG_NONE = 0
PRG_FOOTBALL = 1
PRG_WALL_FOLLOW = 2
PRG_SUMO = 3
# If adding programs, remember to update `select_program`


CURRENT_PROGRAM = PRG_NONE

def set_program(prg):
    global CURRENT_PROGRAM
    if prg in (PRG_NONE, PRG_FOOTBALL, PRG_WALL_FOLLOW, PRG_SUMO):
        CURRENT_PROGRAM = prg
    else:
        CURRENT_PROGRAM = PRG_NONE
    return CURRENT_PROGRAM

def ping(*_): #Ping
    return CURRENT_PROGRAM #TODO: Add battery/others


add_callback(ping)
add_callback(set_program)

# TODO: Add battery callback
# TODO: Add football callback


try:
    while True:
        udp_task()
finally:
    close_socket()


