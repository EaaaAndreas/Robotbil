# src/connectivity/_porting.py

__all__ = ["udp_task", "add_callback", "close_socket"] # Sets what functions are imported when doing `import *`

import socket
import sys
__IS_MPY = sys.implementation.name == "micropython"

# ============================== Setup ==============================
connected = False
_remote_addr:tuple[str,int]|None = None
_connection_timeout_ms = 5000
timer = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock.connect(('8.8.8.8', 80))
    print(f"[UDP] Opened socket on '{sock.getsockname()}'")
except:
    pass


sock.bind(('0.0.0.0', 54321))
sock.settimeout(0)

def close_socket():
    sock.close()



# ============================== Handle OS (dev) ==============================
if __IS_MPY:
    from time import ticks_ms, ticks_diff
else:
    from time import time_ns
    def ticks_ms() -> int:
        return int(time_ns() / 1000)
    def ticks_diff(t0:int, t1:int):
        return t0 - t1


# ============================== Callbacks ==============================

callbacks = dict()

def get_all_commands(timeout):
    return b';'.join([f'{key}{cb.__name__}'.encode('ascii') for key, cb in callbacks.items()])

callbacks[0] = get_all_commands

def set_timeout(timeout):
    global _connection_timeout_ms
    if timeout != 0: # Call set_timeout(0) to get timeout value instead of setting
        _connection_timeout_ms = timeout
    return _connection_timeout_ms

def add_callback(cb):
    global callbacks
    cmd = max(list(callbacks.keys())) + 1
    callbacks[cmd] = cb

add_callback(set_timeout)

def send(seq:bytes, message:bytes):
    print(f"[UDP] Sending {seq}{message}")
    sock.sendto(seq + message, _remote_addr)

def handle_message(data:bytes, addr:tuple):
    global _remote_addr, connected
    if len(data) > 2:
        seq = data[:2]
        data = data[2:]
        print(seq, data)
        if connected: # The unit is connected
            if data[0] in callbacks.keys():
                send(seq, callbacks[data[0]](data[1:]))
        elif _remote_addr is not None: # The unit is establishing a connection
            if addr == _remote_addr and data == b'REQUEST':
                send(seq, b'ACCEPT')
                connected = True
        else: # The unit has no connection
            if seq == b'\x00\x00' and data == b'DISCOVER':
                print(f"[UDP] Received discover from '{addr}'")
                _remote_addr = addr
                send(seq, b'OFFER')

def udp_task():
    try:
        message = sock.recvfrom(1024)
        if message is not None:
            print(f"[UDP] Received '{message}'")
            handle_message(*message)
    except OSError:
        pass

if __name__ == '__main__':
    if __IS_MPY:
        from connectivity.net_setup import init_wlan, wlan
        init_wlan()
        while not wlan.isconnected():
            pass
    def ping():
        return "pong"
    add_callback(ping)
    try:
        while True:
            udp_task()
    finally:
        sock.close()