from time import sleep
from senor import tof
from motor import *

#################################################################
# CONFIG
#################################################################
SM_TICK_MS        = 100
DESIRED_DISTANCE  = 200
WALL_DETECT       = 500
THRESHOLD         = 20

#################################################################
# GLOBALS
#################################################################
DISTANCE = 0

#################################################################
# STATES
#################################################################
STATE_INIT         = 0
STATE_SEARCH_WALL  = 1
STATE_FOLLOW_WALL  = 2

#################################################################
# EVENTS
#################################################################
EVENT_INIT_OK                = True
EVENT_TOO_FAR_FROM_WALL      = False
EVENT_TOO_CLOSE_TO_WALL      = False
EVENT_IN_THRESHOLD_OF_WALL   = False
EVENT_WALL_LOST              = False

#################################################################
# START STATE
#################################################################
smActiveState = STATE_INIT

#################################################################
# MOTOR ACTIONS
#################################################################

def action_search_wall():
    print("ACTION: Searching wall")
    turn_right(40)


def action_drive_straight():
    print("ACTION: Drive straight")
    drive(60)


def action_adjust_left():
    print("ACTION: Adjust left (too close)")
    turn_left(60)


def action_adjust_right():
    print("ACTION: Adjust right (too far)")
    turn_right(60)


#################################################################
# SENSOR UPDATE
#################################################################
def update_sensors():
    global DISTANCE
    DISTANCE = tof()


#################################################################
# EVENT CHECK
#################################################################
def check_wall_events():
    global EVENT_TOO_FAR_FROM_WALL
    global EVENT_TOO_CLOSE_TO_WALL
    global EVENT_IN_THRESHOLD_OF_WALL
    global EVENT_WALL_LOST

    # Reset events
    EVENT_TOO_FAR_FROM_WALL    = False
    EVENT_TOO_CLOSE_TO_WALL    = False
    EVENT_IN_THRESHOLD_OF_WALL = False
    EVENT_WALL_LOST            = False

    if DISTANCE > WALL_DETECT:
        EVENT_WALL_LOST = True

    elif DISTANCE > DESIRED_DISTANCE + THRESHOLD:
        EVENT_TOO_FAR_FROM_WALL = True

    elif DISTANCE < DESIRED_DISTANCE - THRESHOLD:
        EVENT_TOO_CLOSE_TO_WALL = True

    else:
        EVENT_IN_THRESHOLD_OF_WALL = True


#################################################################
# STATE MACHINE LOOP
#################################################################
while True:

    update_sensors()
    check_wall_events()

    #############################################################
    # STATE_INIT
    #############################################################
    if smActiveState == STATE_INIT:

        if EVENT_INIT_OK:
            print("INIT OK - SEARCH WALL")
            smActiveState = STATE_SEARCH_WALL
            EVENT_INIT_OK = False


    #############################################################
    # STATE_SEARCH_WALL
    #############################################################
    elif smActiveState == STATE_SEARCH_WALL:

        action_search_wall()

        if not EVENT_WALL_LOST:
            print("Wall found - FOLLOW")
            smActiveState = STATE_FOLLOW_WALL


    #############################################################
    # STATE_FOLLOW_WALL
    #############################################################
    elif smActiveState == STATE_FOLLOW_WALL:

        if EVENT_WALL_LOST:
            print("Wall lost - SEARCH WALL")
            smActiveState = STATE_SEARCH_WALL

        elif EVENT_TOO_FAR_FROM_WALL:
            action_adjust_right()

        elif EVENT_TOO_CLOSE_TO_WALL:
            action_adjust_left()

        elif EVENT_IN_THRESHOLD_OF_WALL:
            action_drive_straight()


    sleep(SM_TICK_MS / 1000)