# /main.py
from connectivity.porting import *
from football import *
from battery import battery_status, bat_update

PRG_SHT_DWN = -1
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

def ping(*_):
    # Return car parameters
    return CURRENT_PROGRAM #TODO: Add battery/others

def get_battery_status():
    return battery_status

add_callback(ping)
add_callback(set_program)
add_callback(get_battery_status)
add_callback(bat_update)

for cb in fb_callbacks:
    # Add football callbacks
    add_callback(cb)



try:
    while True:
        udp_task()
finally:
    close_socket()


