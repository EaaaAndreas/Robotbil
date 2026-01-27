# /boot.py
from connectivity.network import *
from umachine import Pin
import webrepl

"""
Denne fil køres inden alt andet.
Bruges til ting der skal sættes op, før alt andet (fx. internet)
"""
# MAC: 88:A2:9E:83


# Opret forbindelse til netværket
init_wlan()

# Tænd LED'en på boardet, så vi kan se at den er klar
board_led = Pin("LED", Pin.OUT, value=1)

# Start WEBREPL
webrepl.start(password="WS69")
