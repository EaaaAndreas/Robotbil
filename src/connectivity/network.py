# src/connectivity/network.py
import umachine as machine
from network import WLAN

wlan = WLAN()

def init_wlan(ssid="ITEK 1st", password="itekf25v", hostname="Shitbox"):
    global wlan

    if wlan.isconnected() and wlan.config("ssid") == ssid:
        return

    if wlan.active():
        wlan.active(False)

    wlan.config(interface_id=wlan.IF_STA, hostname=hostname)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect("ITEK 1st", "itekf25v")

    while not wlan.isconnected():
        machine.idle()

def init_ap(name="Shitbox", password="WS69"):
    global wlan

    if wlan.active():
        if wlan.isconnected():
            wlan.disconnect()
        wlan.active(False)
    wlan.config(interface_id=wlan.IF_AP, name=name, password=password)

    wlan.active(True)
