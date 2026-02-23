# /main.py
from connectivity.porting import *
from football import *
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
        stop_football()
    motor.stop()

def set_program(prg):
    global CURRENT_PROGRAM
    if prg != CURRENT_PROGRAM:
        stop_program()
    if prg == PRG_FOOTBALL:
        CURRENT_PROGRAM = PRG_FOOTBALL
        start_football()
    elif prg == PRG_WALL_FOLLOW:
        pass
    elif prg == PRG_SUMO:
        pass
    elif prg == PRG_SHT_DWN:
        pass
    else:
        CURRENT_PROGRAM = PRG_NONE
    return 'B', CURRENT_PROGRAM

def ping(*_):
    # Return car parameters
    return 'BB', CURRENT_PROGRAM, battery_status #TODO: Add battery/others

def get_battery_status():
    return 'B', battery_status

add_callback(ping)
add_callback(set_program)
add_callback(get_battery_status)
add_callback(bat_update)
add_callback(fb_control)



try:
    while True:
        udp_task()
        if not connected:
            stop_program()

finally:
    close_socket()


