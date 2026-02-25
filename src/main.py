# /main.py
from connectivity.porting import *
from football import football as fb
from battery import battery_status, bat_update
import motor

PRG_SHT_DWN = -1
PRG_NONE = 0
PRG_FOOTBALL = 1
PRG_WALL_FOLLOW = 2
PRG_SUMO = 3
# If adding programs, remember to update `select_program`


CURRENT_PROGRAM = PRG_NONE

def stop_program():
    if CURRENT_PROGRAM == PRG_FOOTBALL:
        fb.stop_football()
    motor.stop()

def set_program(prg):
    global CURRENT_PROGRAM
    if prg != CURRENT_PROGRAM:
        stop_program()
    if prg == PRG_FOOTBALL:
        CURRENT_PROGRAM = PRG_FOOTBALL
        fb.start_football()
    elif prg == PRG_WALL_FOLLOW:
        pass
    elif prg == PRG_SUMO:
        pass
    elif prg == PRG_SHT_DWN:
        pass
    else:
        CURRENT_PROGRAM = PRG_NONE
    return 'B', CURRENT_PROGRAM

@command
def program_select(prg:bytes):
    prgs = {
        b'NN': 0,
        b'FB': 1,
        b'WF': 2,
        b'SU': 3
    }
    if prg in prgs:
        set_program(prgs[prg])
    else:
        set_program(PRG_NONE)
    return [k for k, v in prgs.items() if v == CURRENT_PROGRAM][0]

program_select.name = 'PRG'


@command
def football_control(*args, **kwargs):
    return fb.fb_control(*args, **kwargs)

football_control.name = 'FBC'

try:
    print('Running main loop')
    while True:
        try:
            udp_task()
            if CURRENT_PROGRAM == PRG_FOOTBALL:
                fb.fb_task()
            elif CURRENT_PROGRAM == PRG_WALL_FOLLOW:
                pass
            elif CURRENT_PROGRAM == PRG_SUMO:
                pass
        except ConnectionTimeout:
            stop_program()

finally:
    close_socket()


