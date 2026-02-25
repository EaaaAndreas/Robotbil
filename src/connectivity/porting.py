# src/connectivity/_porting.py
import struct
__all__ = ["ConnectionTimeout","udp_task", "close_socket", "connected", "test", "command"] # Sets what functions are imported when doing `import *`
from time import ticks_ms, ticks_diff
import socket
import sys
__IS_MPY = sys.implementation.name == "micropython"
print("UDP - init")
default_params = {}
params = []

class ConnectionTimeout(BaseException):
    pass

# ============================== Setup ==============================
connected = False
_remote_addr:tuple[str,int]|None = None
_connection_timeout_ms = 50000
_timer_ms = ticks_ms()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 54321))

#try:
#    sock.connect(('8.8.8.8', 80))
#    print(f"[UDP] Opened socket on '{sock.getsockname()}'")
#except:
#    pass
sock.settimeout(0)


def close_socket():
    sock.close()

"""

# ============================== Handle OS (dev) ==============================
if __IS_MPY:
    from time import ticks_ms, ticks_diff
else:
    from time import time_ns
    def ticks_ms() -> int:
        return int(time_ns() / 1000)
    def ticks_diff(t0:int, t1:int):
        return t0 - t1

"""
def update_timer():
    global _timer_ms
    _timer_ms = ticks_ms()

# ============================== Callbacks ==============================


commands = []

def get_command(name:bytes):
    for cmd in commands:
        if cmd.name == name:
            return cmd
    return None

class command:
    isdefault = False
    def __init__(self, fn):
        self.fn = fn
        self.name = fn.__name__[:3]
        commands.append(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value:str|bytes):
        if len(value) != 3:
            raise ValueError(f"Name must be 3 letters")
        if isinstance(value, str):
            value = value.encode('ascii')
        self._name = value.upper()

    def __call__(self, cmd:bytes):
        global default_params, params
        if self.isdefault:
            for key, value in self.fn(cmd.lstrip(self.name)):
                default_params[key] = value
        else:
            print(self.name)
            params.append(self.name + self.fn(cmd.lstrip(self.name)) or b'')



def send(seq:bytes, message:bytes):
    print(f"[UDP] Sending {seq}{message}")
    sock.sendto(seq + message, _remote_addr)

def send_params(seq):
    message = b'$'.join([k+v for k,v in default_params])
    if len(params):
        message += b'$'.join(params)
        params.clear()
    send(seq, message)

@command
def ping(*_):
    pass

def handle_commands(data:bytes):
    for dat in data.split(b'$'):
        cmd = get_command(dat[:3])
        if cmd is not None:
            cmd(dat)


def handle_message(data:bytes, addr:tuple):
    global _remote_addr, connected
    if len(data) > 2:
        seq = data[:2]
        data = data[2:]
        if connected: # The unit is connected
            handle_commands(data)
            send_params(seq)
        elif _remote_addr is not None: # The unit is establishing a connection
            if addr == _remote_addr and data == b'REQUEST':
                send(seq, b'ACCEPT')
                connected = True
                update_timer()
        else: # The unit has no connection
            if seq == b'\x00\x00' and data == b'DISCOVER':
                print(f"[UDP] Received discover from '{addr}'")
                _remote_addr = addr
                send(seq, b'OFFER')

def udp_task():
    global connected, _remote_addr
    try:
        message = sock.recvfrom(1024)
        if message is not None:
            print(f"[UDP] Received '{message}'")
            handle_message(*message)
    except OSError:
        pass
    if connected and ticks_diff(ticks_ms(), _timer_ms) > _connection_timeout_ms:
        print('[UDP] Dropping connection')
        send(b'\xff\xff', b'CTO') # ConnectionTimeOut
        connected = False
        _remote_addr = None
        raise ConnectionTimeout

def test():
    try:
        while True:
            udp_task()
    finally:
        sock.close()

if __name__ == '__main__':
    if __IS_MPY:
        from connectivity.net_setup import init_wlan, wlan
        init_wlan()
        while not wlan.isconnected():
            pass
    #def ping():
    #    return "pong"
    #add_callback(ping)
    test()