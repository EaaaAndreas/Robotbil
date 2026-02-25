from time import sleep
from sensor.tof import tof
from motor import motortest as motor
#################################################################
# CONFIG
#################################################################
SM_TICK_MS        = 10
DESIRED_DISTANCE  = 200
WALL_DETECT       = 500
BASE_SPEED        = 60
SENSITIVITY       = 0.4

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
EVENT_WALL_LOST              = False

#################################################################
# START STATE
#################################################################
smActiveState = STATE_INIT


#################################################################
# ACTIONS (Using your DCMotor objects directly)
#################################################################

def action_search_wall():
    print("ACTION: Searching wall")
    motor.left_motor.set_speed(40)
    motor.right_motor.set_speed(10)


def action_follow_wall():
    global DISTANCE

    error = DESIRED_DISTANCE - DISTANCE
    turn  = SENSITIVITY * error

    left_speed  = BASE_SPEED - turn
    right_speed = BASE_SPEED + turn

    # clamp
    left_speed  = max(-100, min(100, int(left_speed)))
    right_speed = max(-100, min(100, int(right_speed)))

    print("L:", left_speed, "R:", right_speed)

    motor.left_motor.set_speed(left_speed)
    motor.right_motor.set_speed(right_speed)


def action_stop():
    print("ACTION: Stop")
    motor.stop()


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
    global EVENT_WALL_LOST

    # Reset events
    EVENT_WALL_LOST     = False

    if DISTANCE > WALL_DETECT:
        EVENT_WALL_LOST = True


#################################################################
# STATE MACHINE LOOP
#################################################################
def test():
    global smActiveState, EVENT_INIT_OK
    print('Testing WF')
    while True:

        update_sensors()
        check_wall_events()
        print(DISTANCE)
        #############################################################
        # STATE_INIT
        #############################################################
        if smActiveState == STATE_INIT:

            if EVENT_INIT_OK:
                print("INIT - SEARCH WALL")
                action_stop()
                smActiveState = STATE_SEARCH_WALL
                EVENT_INIT_OK = False


        #############################################################
        # STATE_SEARCH_WALL
        #############################################################
        elif smActiveState == STATE_SEARCH_WALL:

            if EVENT_WALL_LOST:
                action_search_wall()

            else:
                print("Wall found - FOLLOW")
                smActiveState = STATE_FOLLOW_WALL


        #############################################################
        # STATE_FOLLOW_WALL
        #############################################################
        elif smActiveState == STATE_FOLLOW_WALL:

            if EVENT_WALL_LOST:
                print("Wall lost - SEARCH")
                smActiveState = STATE_SEARCH_WALL

            else:
                action_follow_wall()


        sleep(SM_TICK_MS / 1000)