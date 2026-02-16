# src/connectivity/network.py
import umachine as machine
import network as nw
import json
import uos as os
from ._crypto import encrypt, decrypt
import ubinascii
from time import sleep_ms


# Lav wlan som en global variabel, så den kan tilgås fra andre scripts
wlan = nw.WLAN()

SAVE_FILE_DIR = '/cfg/networks.json'
_netstats = ['Idle', 'Connecting', '', 'Got IP', 'Wrong Password', 'No AP Found', 'Connect Fail']


def _check_file(path:str) -> bool|None:
    """
    Tjekker om en fil findes.
    :param path: stien til filen
    :type path: str
    :return:
        - True, hvis filen findes og har indhold
        - None, hvis den findes, men er tom
        - False, hvis den ikke findes
    :rtype: bool | None
    """
    try:
        # Tjek stats for filen
        st = os.stat(path) # -> (mode, _, _, _, _, _, size, access time, modify time, change/create time)
        if not st or not st[6] > 0:
            if st[0] == 32768: # 32768 = regular file. 16384 = directory
                return None
            return False
        return True
    except OSError:
        return False


def get_known_networks():
    """
    En generator funktion (brug `list(get_known_networks)` for at få en liste,
    eller bare `for net in get_known_networks()` for at iterere over netværkene), som returnerer alle kendte netværks
    ssid og password (eller None, hvis der ikke er kode på).
    :return: En tuple med (SSID, Password, BSSID) eller None, hvis der ikke er gemt nogen netværk
    :rtype: tupe[str, str|None, str|None] | None
    """
    # Tjek om filen eksisterer
    if not _check_file(SAVE_FILE_DIR):
        # Hvis ikke, er der ikke nogen gemte netværk
        return
    # Læs filen
    with open(SAVE_FILE_DIR, 'r', encoding='utf-8') as f:
        networks = json.load(f)
    for ssid, val in networks.items():
        # Separér kode og BSSID og afkod kodeordet.
        pss, bssid = val
        pss = decrypt(ubinascii.a2b_base64(pss)).decode('utf-8')
        if pss == '\x00':
            # Konverter null til None
            pss = None
        yield ssid, pss, bssid
    return


def save_network(ssid:str|bytes, password:str|bytes|None, bssid:str|bytes|None=None) -> None:
    """
    Gem et netværk og kodeordet dertil.
    Kodeordet bliver krypteret og gemt, sammen med SSID'et, i filen '/networks.json'.
    :param ssid: SSID på det netværk du gerne vil gemme.
    :type ssid: str|bytes
    :param password: Kodeordet til det netværk der skal gemmes. None, hvis der ikke er et kodeord.
    :type password: str|bytes|None
    :param bssid: Det foretrukne bssid, på det hotspot der skal forbindes til. Default: None
    :type bssid: str|bytes|None
    :return:
    :rtype:
    """
    if password is None: # Undgå at et password bliver sat som 'None'
        password = '\x00'
    # Tjek om filen findes
    if _check_file(SAVE_FILE_DIR):
        # Læs gemte netværk
        with open(SAVE_FILE_DIR, 'r', encoding="utf-8") as f:
            networks = json.load(f)
    else:
        networks = {}
    # Tilføj det nye netværk
    networks[ssid] = (ubinascii.b2a_base64(encrypt(bytes(password, 'utf-8'))), bssid)
    # Gem den opdaterede dict
    with open(SAVE_FILE_DIR, 'w', encoding="utf-8") as f:
        json.dump(networks, f)


def init_wlan(ssid:str=None, password:str=None, bssid:str|None=None, hostname:str="shitbox", auto_save:bool=True) -> None:
    """
    Opretter forbindelse til et netværk
    :param ssid: ssid'et på det netværk der skal oprettes forbindelse til.
    :type ssid: str
    :param password: kodeord
    :type password: str
    :param bssid: Hvis der skal bruges en bestemt AP, angives mac-addressen her. Ellers None
    :type bssid: str|None
    :param hostname: Maskinens hostname på netværket (bliver ikke synligt i eks. Advanced IP scanner)
    :type hostname: str
    :param auto_save: Hvis True, gemmes netværket automatisk. Default: True
    :type auto_save: bool
    :return: None
    """
    global wlan
    # Sæt wlan til at oprette forbindelse til et netværk
    wlan = nw.WLAN(nw.WLAN.IF_STA)

    # Tjek om vi allerede har forbindelse
    if wlan.isconnected() and (ssid is None or wlan.config("ssid") == ssid):
        return

    # Tjek om wlan er tændt
    if wlan.active():
        # Sluk, for at undgå ukendte fejl
        wlan.active(False)

    # Opsæt og tænd wlan
    wlan.config(hostname=hostname)
    wlan.active(True)


    if ssid is not None: # Der er angivet et specifikt netværk
        wlan.connect(ssid, password, bssid=bssid)
        auto_save = False
    else: # Find tilgængeligt kendt netværk
        # Find alle tilgængelige netværk
        scan = wlan.scan()
        # Loop over kendte netværk
        for ssid, password, bssid in get_known_networks():
            # Loop over tilgængelige netværk
            for net in scan:
                if ssid == net[0].decode(): # Det er et netværk vi kender
                    if bssid: # Vil vi på et bestemt AP?
                        if bssid == net[1].decode(): # Er det det angivne AP
                            wlan.connect(ssid, password, bssid=bssid)
                    else:
                        wlan.connect(ssid, password)

    # Vent på at der er forbindelse
    # While loopet kører kun så længe `wlan` er i gang med at oprette forbindelse.
    # Hvis `wlan` ikke er sat til at forbinde, eller allerede er forbundet, etc. springes det over.
    while wlan.status() == nw.STAT_CONNECTING:
        machine.idle() # Reducér clock speed

    if auto_save and wlan.isconnected():
        save_network(ssid, password, bssid)
    sleep_ms(5)
    # Log status
    print("[Network Connection] status", _netstats[wlan.status()])


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

    # Ungå tilfældige fejl
    if wlan.isconnected():
        wlan.disconnect()
    if wlan.active():
        wlan.active(False)

    # Opsæt lan antennen til access point
    wlan = nw.WLAN(nw.WLAN.IF_AP)

    # Sluk AP imens det sættes op (den burde være slukket efter `wlan = nw.WLAN(nw.WLAN.IF_AP)`)
    if wlan.active():
        wlan.active(False)

    wlan.config(interface_id=wlan.IF_AP, name=name, password=password)

    wlan.active(True)

    print("[Network Connection] status", _netstats[wlan.status()])


def get_ip():
    return wlan.ipconfig('addr4')[0]


def get_default_gateway():
    ipa, subnet = wlan.ipconfig('addr4')
    # IP:           00001010.01101110.00000000.01000110
    # Subnet:       11111111.11111111.11111111.00000000
    # IP & Subnet:  00001010.01101110.00000000.00000000
    return '.'.join([str(int(i) & int(s)) for i, s in zip(ipa.split('.'), subnet.split('.'))])


def get_broadcast_address():
    ipa, subnet = wlan.ipconfig('addr4')
    # IP:                       00001010.01101110.00000000.01000110
    # Subnet:                   11111111.11111111.11111111.00000000
    # ~Subnet & 0xFF:           00000000.00000000.00000000.11111111
    # IP | (~subnet & 0xFF):    00001010.01101110.00000000.11111111
    return '.'.join([str(int(i) | (~int(s) & 0xFF)) for i, s in zip(ipa.split('.'), subnet.split('.'))])