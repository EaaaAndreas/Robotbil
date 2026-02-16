# src/connectivity/porting.py
import usocket as socket
from usocket import AF_INET, SOCK_DGRAM
from net_setup import wlan, get_ip, get_broadcast_address

IP_ADDR: str|None = None
PORT = 50001
_addr = (IP_ADDR, PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

_bound = False
_connected = False

def is_bound() -> bool:
    """
    Check if the socket is bound to the port.
    :return: True if the socket is bound, else False.
    :rtype: bool
    """
    return _bound

def is_connected() -> bool:
    """
    Check if the unit has an established connection to a client.
    :return: True if the unit is connected to a client, else False.
    :rtype: bool
    """
    return _connected

def set_address(ip_addr:str, port:int|None=None) -> None:
    global IP_ADDR, PORT, _addr
    IP_ADDR = ip_addr
    if port is not None:
        PORT = PORT
    _addr = (IP_ADDR, port)


def _init() -> None:
    """
    Initialize the socket. This checks if the socket is already open.
    :return: None
    """
    global sock, _bound, _connected, IP_ADDR
    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if IP_ADDR is None:
        set_address(get_ip())
    if _bound:
        if sock.getsockname() == _addr:
            return
        sock.bind(_addr)
        _bound = True

def broadcast():
    global _connected
    if _connected:
        return
    _init()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.2)
    while not _connected:
        sock.sendto(b'Shitbox',(get_broadcast_address(), PORT))
