from time import sleep_ms
from time import sleep
from sensor.tof import tof
from motor import motortest as motor
from sensor.ir import ir

#################################################################
# CONFIG
#################################################################
SM_TICK_MS = 10
OBJECT_DETECT = 1000  # mm
BASE_SPEED = 55
ATTACK_SPEED = 50
TURN_SPEED = 32
REVERSE_SPEED = -60

SEARCH_TIMEOUT = 40  # 200 ticks ≈ 2 seconds

#################################################################
# STATES
#################################################################
STATE_SEARCH = 0
STATE_ATTACK = 1
STATE_EDGE_ESCAPE = 2
STATE_ROAM = 3

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
    print("search")
    motor.left_motor.set_speed(TURN_SPEED)
    motor.right_motor.set_speed(-TURN_SPEED)


def action_attack():
    print("attack")
    motor.left_motor.set_speed(int(ATTACK_SPEED * 0.8))
    motor.right_motor.set_speed(ATTACK_SPEED)
    sleep_ms(50)


def action_roam():
    # Slight curve so we scan while moving
    print("roam")
    motor.left_motor.set_speed(BASE_SPEED)
    motor.right_motor.set_speed(BASE_SPEED - 10)


def action_escape():
    # Reverse
    print("escape")
    motor.left_motor.set_speed(REVERSE_SPEED)
    motor.right_motor.set_speed(REVERSE_SPEED)
    sleep_ms(650)
    motor.left_motor.set_speed(TURN_SPEED)
    motor.right_motor.set_speed(-TURN_SPEED)
    sleep_ms(150)


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

def sumo_task():
    global smActiveState, search_counter

    print("Starting SUMO mode")

    update_sensors()

    #############################################################
    # EDGE DETECTION (HIGHEST PRIORITY)
    #############################################################
    if EDGE_DETECTED:
        smActiveState = STATE_EDGE_ESCAPE

    #############################################################
    # STATE: SEARCH
    #############################################################
    if smActiveState == STATE_SEARCH:

        if DISTANCE < OBJECT_DETECT:
            smActiveState = STATE_ATTACK
            search_counter = 0

        else:
            action_search()
            search_counter += 1
            print(search_counter)

            if search_counter > SEARCH_TIMEOUT:
                smActiveState = STATE_ROAM
                search_counter = 0

    #############################################################
    # STATE: ROAM
    #############################################################
    elif smActiveState == STATE_ROAM:

        if DISTANCE < OBJECT_DETECT:
            smActiveState = STATE_ATTACK

        else:
            action_roam()

    #############################################################
    # STATE: ATTACK
    #############################################################
    elif smActiveState == STATE_ATTACK:

        if DISTANCE > OBJECT_DETECT:
            smActiveState = STATE_SEARCH
        else:
            action_attack()

    #############################################################
    # STATE: EDGE ESCAPE
    #############################################################
    elif smActiveState == STATE_EDGE_ESCAPE:

        sleep_ms(100)
        action_escape()
        smActiveState = STATE_SEARCH
        search_counter = 0

    sleep(SM_TICK_MS / 1000)


def sumo_test():
    while True:
        sumo_task()


if __name__ == '__main__':
    sumo_test()