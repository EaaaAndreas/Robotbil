# /boot.py
from connectivity.net_setup import init_wlan
from umachine import Pin
import webrepl

"""
Denne fil køres inden alt andet.
Bruges til ting der skal sættes op, før alt andet (fx. internet)
"""
# MAC: 88:A2:9E:83


board_led = Pin("LED", Pin.OUT, value=0)

# Opret forbindelse til netværket
init_wlan()

# Tænd LED'en på boardet, så vi kan se at den er klar
board_led.on()

# Start WEBREPL
webrepl.start(password="WS69")
