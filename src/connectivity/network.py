# src/connectivity/network.py
import umachine as machine
from network import WLAN


wlan = WLAN()

def init_wlan(ssid:str="ITEK 1st", password:str="itekf25v", hostname="Shitbox") -> None:
    """
    Opretter forbindelse til et netværk
    :param ssid: ssid'et på det netværk der skal oprettes forbindelse til.
    :type ssid: str
    :param password: kodeord
    :type password:
    :param hostname:
    :type hostname:
    :return:
    :rtype:
    """
    global wlan
    wlan = WLAN(WLAN.IF_STA)
    if wlan.isconnected() and wlan.config("ssid") == ssid:
        return

    if wlan.active():
        wlan.active(False)

    #wlan.config(interface_id=wlan.IF_STA, hostname=hostname)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(ssid, password)

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
