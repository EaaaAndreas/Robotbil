# src/connectivity/network.py
import umachine as machine
from network import WLAN

# Lav wlan som en global variabel, så den kan tilgåes fra andre scripts
wlan = WLAN()

def init_wlan(ssid:str="ITEK 1st", password:str="itekf25v", hostname:str="Shitbox") -> None:
    """
    Opretter forbindelse til et netværk
    :param ssid: ssid'et på det netværk der skal oprettes forbindelse til.
    :type ssid: str
    :param password: kodeord
    :type password: str
    :param hostname: Maskinens hostname på netværket (bliver ikke synligt i eks. Advanced IP scanner)
    :type hostname: str
    :return: None
    """
    global wlan
    # Sæt wlan til at oprette forbindelse til et netværk
    wlan = WLAN(WLAN.IF_STA)

    # Tjek om vi allerede har forbindelse
    if wlan.isconnected() and wlan.config("ssid") == ssid:
        return

    # Tjek om wlan er tændt
    if wlan.active():
        # Sluk, for at undgå ukendte fejl
        wlan.active(False)

    # Opsæt og tænd wlan
    wlan.config(hostname=hostname)
    wlan.active(True)

    # Opret forbindelse til netværket
    if not wlan.isconnected():
        wlan.connect(ssid, password)

    # Vent på at der er forbindelse
    while not wlan.isconnected():
        machine.idle()

def init_ap(name:str="Shitbox", password:str="WS69") -> None:
    """
    Opret et access point, så der kan forbindes direkte til Picoen.
    :param name: Navnet på access point
    :type name: str
    :param password: Koden til netværket
    :type password: str
    :return: None
    """
    global wlan

    # Opsæt lan antennen til access point
    wlan = WLAN(WLAN.IF_AP)

    if wlan.active():
        if wlan.isconnected():
            wlan.disconnect()
        wlan.active(False)
    wlan.config(interface_id=wlan.IF_AP, name=name, password=password)

    wlan.active(True)
