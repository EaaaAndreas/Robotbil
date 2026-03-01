# /main.py
from connectivity.porting import *
from football import football as fb
from wallfollow import wallfollow as wf
from battery import battery_status, bat_update
import motor

from time import sleep_ms

sleep_ms(500)
print("Main")
class Program:
    shutdown = b'SD'
    idle = b'NN'
    football = b'FB'
    wallfollow = b'WF'
    sumo = b'SU'
    all = [shutdown, idle, football, wallfollow, sumo]
# If adding programs, remember to update `select_program`

CURRENT_PROGRAM = Program.idle


def stop_program():
    if CURRENT_PROGRAM == Program.football:
        fb.stop_football()
    motor.stop()

def set_program(prg):
    print("Setting program", prg)
    global CURRENT_PROGRAM
    if prg != CURRENT_PROGRAM:
        stop_program()
    if prg == Program.football:
        CURRENT_PROGRAM = Program.football
        fb.start_football()
    elif prg in Program.all:
        CURRENT_PROGRAM = prg
    else:
        CURRENT_PROGRAM = Program.idle
    return CURRENT_PROGRAM,

def program_select(prg:bytes):
    print(prg, Program.all)
    if prg in Program.all:
        set_program(prg)
    else:
        set_program(Program.idle)
    return CURRENT_PROGRAM,

def ping_data():
    return CURRENT_PROGRAM,

Command(program_select, '2s', 'PRG')
Command(fb.fb_control, 'sBB', 'FBC')
Command(bat_update, 'B', 'BAT')
Command(ping_data, '2s', 'PIN')

try:
    print('Running main loop')
    while True:
        try:
            udp_task()
            if isconnected():
                if CURRENT_PROGRAM == Program.football:
                    #fb.fb_task()
                    pass
                elif CURRENT_PROGRAM == Program.wallfollow:
                    wf.wf_task()
                elif CURRENT_PROGRAM == Program.sumo:
                    pass
        except ConnectionTimeout:
            stop_program()

finally:
    close_socket()


