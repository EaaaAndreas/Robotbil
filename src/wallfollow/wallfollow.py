from time import sleep
from sensor.tof import tof
from motor import motortest as motor

#################################################################
# CONFIG
#################################################################
SM_TICK_MS = 10
DESIRED_DISTANCE = 400
WALL_DETECT = 600
BASE_SPEED = 100
P_VALUE = 0.2
I_VALUE = 0.8

#################################################################
# GLOBALS
#################################################################
DISTANCE = 0
previous_error = 0
#################################################################
# STATES
#################################################################
STATE_SEARCH_WALL = 0
STATE_FOLLOW_WALL = 1

#################################################################
# EVENTS
#################################################################
EVENT_WALL_LOST = False

#################################################################
# START STATE
#################################################################
smActiveState = STATE_SEARCH_WALL


#################################################################
# ACTIONS
#################################################################

def action_search_wall():
    print("ACTION: Searching wall")
    motor.left_motor.set_speed(100)
    motor.right_motor.set_speed(40)


def action_follow_wall():
    global DISTANCE, previous_error

    #   Calculating the difference between the desired distance and the actual distance to the wall
    error = DESIRED_DISTANCE - DISTANCE

    #   immediate correction to the turning. The bigger the error, the bigger the turn
    P = P_VALUE * error

    #   calculating how fast the error is changing (RATE_OF_CHANGE).
    #   Rapid change increases steering correction, helping in sharp corners.
    RATE_OF_CHANGE = error - previous_error
    I = I_VALUE * RATE_OF_CHANGE

    #   combining P (position correction) and I (change-based correction)
    turn = P + I

    #   Converting the Turn into the motor speeds. if turn is positive: turns left, if turn is negative: turns right
    left_speed = BASE_SPEED - turn
    right_speed = BASE_SPEED + turn

    #   clamping motor speeds, so they stay between -100 and 100
    left_speed = max(-100, min(100, int(left_speed)))
    right_speed = max(-100, min(100, int(right_speed)))

    #   Prints the speed on each motor
    print("L:", left_speed, "R:", right_speed)

    #   Sends signal to the motors
    motor.left_motor.set_speed(left_speed)
    motor.right_motor.set_speed(right_speed)

    #   Sets the error to be the previous error for the next loop
    previous_error = error


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

    # Reset event
    EVENT_WALL_LOST = False

    if DISTANCE > WALL_DETECT:
        EVENT_WALL_LOST = True


#################################################################
# STATE MACHINE LOOP
#################################################################
def wf_task():
    global smActiveState
    print('Testing WF')

    update_sensors()
    check_wall_events()
    print(DISTANCE)

    #############################################################
    # STATE_SEARCH_WALL
    #############################################################
    if smActiveState == STATE_SEARCH_WALL:

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


def wf_test():
    while True:
        wf_task()


if __name__ == '__main__':
    wf_test()