# /boot.py
from connectivity.network import *
from umachine import Pin
import webrepl

# MAC: 88:A2:9E:83

init_wlan()

board_led = Pin("LED", Pin.OUT, value=1)

webrepl.start(password="WS69")
