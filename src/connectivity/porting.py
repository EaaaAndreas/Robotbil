# src/connectivity/_porting.py
import struct
__all__ = ["ConnectionTimeout","udp_task", "close_socket", "connected", "test", "Command", ] # Sets what functions are imported when doing `import *`
from time import ticks_ms, ticks_diff
import socket
print("UDP - init")

class ConnectionTimeout(BaseException):
    pass

# ============================== Setup ==============================
connected = False
_remote_addr:tuple[str,int]|None = None
_connection_timeout_ms = 5000
_timer_ms = ticks_ms()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 54321))
sock.settimeout(0)


def close_socket():
    sock.close()


def update_timer():
    global _timer_ms
    _timer_ms = ticks_ms()

# ============================== Commands ==============================

commands = {}
class Command:
    _name = b''
    def __init__(self, fn, output_type: str, name: str | bytes):
        self.fn = fn
        self.output_type = output_type
        self.name = name

        self._last_called = ticks_ms()
        commands[name] = self

    @property
    def name(self) -> bytes:
        return self._name

    @name.setter
    def name(self, value:str|bytes):
        if len(value) != 3:
            raise ValueError(f"Command name must be exactly 3 characters. Got '{value}'")
        if isinstance(value, str):
            value = value.encode('ascii')
        if self._name in commands.keys():
            commands.pop(self._name)
        self._name = value
        commands[self._name] = self

    def __call__(self, *args:bytes):
        print(self.name, args)
        ans = tuple(self.fn(*args))
        print(ans)
        return self.name + struct.pack(self.output_type, *ans)


# ============================== Transmitting ==============================

def send(seq:bytes, message:bytes):
    print(f"[UDP] Sending {seq}{message}")
    sock.sendto(seq + message, _remote_addr)


def handle_message(data:bytes, addr:tuple):
    global _remote_addr, connected, _connection_timeout_ms
    if len(data) > 2:
        seq = data[:2]
        data = data[2:]
        if connected: # The unit is connected
            cmd = data[:3]
            data = data[3:]
            if cmd == b'PIN':
                send(seq, b'ACK')
            elif cmd == b'DSC':
                send(seq, b'DSC')
                connected = False
                _remote_addr = None
            else:
                try:
                    send(seq, commands[cmd](data))
                except KeyError:
                    send(seq, b"ERR")
            _connection_timeout_ms = ticks_ms()
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
