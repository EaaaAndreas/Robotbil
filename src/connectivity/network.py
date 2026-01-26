# src/connectivity/network.py
import umachine as machine
from network import WLAN

def init_wlan(ssid="ITEK 1st", password="itekf25v", hostname="Shitbox"):
    wlan = WLAN(WLAN.IF_STA)

    if wlan.active():
        wlan.active(False)

    wlan.config(hostname=hostname)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect("ITEK 1st", "itekf25v")

    while not wlan.isconnected():
        machine.idle()

def init_ap(name="Shitbox", password="WS69"):
    wlan = WLAN(WLAN.IF_AP)

    if wlan.active():
        if wlan.isconnected():
            wlan.disconnect()
        wlan.active(False)
    wlan.config(name=name, password=password)

    wlan.active(True)
