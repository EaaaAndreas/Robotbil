from time import sleep_ms
from time import sleep
from sensor.tof import tof
from motor import motortest as motor
from sensor.ir import ir

#################################################################
# CONFIG
#################################################################
SM_TICK_MS        = 5
OBJECT_DETECT     = 700     # mm
BASE_SPEED        = 60
ATTACK_SPEED      = 50
TURN_SPEED        = 40
REVERSE_SPEED     = -60

SEARCH_TIMEOUT    = 85    # 200 ticks ≈ 2 seconds

#################################################################
# STATES
#################################################################
STATE_SEARCH      = 0
STATE_ATTACK      = 1
STATE_EDGE_ESCAPE = 2
STATE_ROAM        = 3

#################################################################
# GLOBALS
#################################################################
smActiveState = STATE_SEARCH
DISTANCE = 0
EDGE_DETECTED = False
search_counter = 0

#################################################################
# ACTIONS
#################################################################

def action_search():
    motor.left_motor.set_speed(TURN_SPEED)
    motor.right_motor.set_speed(-TURN_SPEED)


def action_attack():
    motor.left_motor.set_speed(ATTACK_SPEED * 0.80)
    motor.right_motor.set_speed(ATTACK_SPEED)


def action_roam():
    # Slight curve so we scan while moving
    motor.left_motor.set_speed(BASE_SPEED)
    motor.right_motor.set_speed(BASE_SPEED - 10)


def action_escape():
    # Reverse
    motor.left_motor.set_speed(REVERSE_SPEED)
    motor.right_motor.set_speed(REVERSE_SPEED)
    sleep_ms(650)


def action_stop():
    motor.stop()

#################################################################
# SENSOR UPDATE
#################################################################

def update_sensors():
    global DISTANCE, EDGE_DETECTED
    DISTANCE = tof()
    EDGE_DETECTED = ir()

#################################################################
# STATE MACHINE
#################################################################

def sumo():
    global smActiveState, search_counter

    print("Starting SUMO mode")

    while True:

        update_sensors()

        #############################################################
        # EDGE DETECTION (HIGHEST PRIORITY)
        #############################################################
        if EDGE_DETECTED:
            print("STATE - EDGE_ESCAPE")
            smActiveState = STATE_EDGE_ESCAPE

        #############################################################
        # STATE: SEARCH
        #############################################################
        if smActiveState == STATE_SEARCH:

            if DISTANCE < OBJECT_DETECT:
                print("STATE - ATTACK")
                smActiveState = STATE_ATTACK
                search_counter = 0

            else:
                action_search()
                search_counter += 1

                if search_counter > SEARCH_TIMEOUT:
                    print("STATE - ROAM")
                    smActiveState = STATE_ROAM
                    search_counter = 0

        #############################################################
        # STATE: ROAM
        #############################################################
        elif smActiveState == STATE_ROAM:

            if DISTANCE < OBJECT_DETECT:
                print("STATE - ATTACK")
                smActiveState = STATE_ATTACK

            else:
                action_roam()

        #############################################################
        # STATE: ATTACK
        #############################################################
        elif smActiveState == STATE_ATTACK:

            if DISTANCE > OBJECT_DETECT:
                print("STATE - SEARCH")
                smActiveState = STATE_SEARCH
            else:
                action_attack()

        #############################################################
        # STATE: EDGE ESCAPE
        #############################################################
        elif smActiveState == STATE_EDGE_ESCAPE:

            sleep_ms(100)
            action_escape()
            print("STATE - SEARCH")
            smActiveState = STATE_SEARCH
            search_counter = 0

        sleep(SM_TICK_MS / 1000)

sumo()