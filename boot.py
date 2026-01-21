# /boot.py

from network import WLAN
from umachine import idle, Pin
from utime import sleep_ms
wlan = WLAN()

if wlan.active():
    wlan.active(False)

wlan.active(True)

if not wlan.isconnected():
    wlan.connect("ITEK 1st", "itekf25v")

while not wlan.isconnected():
    idle()

led = Pin("LED", Pin.OUT)

for i in range(5):
    led.off()
    sleep_ms(20)
    led.on()


import webrepl

webrepl.start()
