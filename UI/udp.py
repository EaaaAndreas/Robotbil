import socket
from threading import *
import queue
import struct
import time


class Command:
    disconnect:bytes = b'DSC'
    program:bytes = b'PRG'
    ping:bytes = b'PIN'
    connection_timeout:bytes = b'CTO'
    battery:bytes = b'BAT'


class RemoteStatus:
    def __init__(self, command, cadence, datatype:str):
        self.command = command
        self.cadence = cadence
        self.datatype = datatype
        self.last_updated = 0
        self._value = None

    @property
    def outdated(self):
        return time.time() - self.last_updated > self.cadence

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = struct.unpack(self.datatype, val)[0]
        self.last_updated = time.time()

REMOTE_NAME = 'shitbox.local'
REMOTE_PORT = 54321

class UDPClient:
    def __init__(self, ping_interval=1.0, reply_timeout=5.0, connect_timeout=10.0, recv_buffer=2048):
        self.ping_interval = ping_interval
        self.reply_timeout = reply_timeout
        self.connect_timeout = connect_timeout
        self.recv_buffer = recv_buffer

        self.battery = RemoteStatus(Command.battery, 5, 'B')

        self.stat_cmds = [self.battery]

        self.sock = None
        self.address = None
        self._remote_addr = None

        self._send_queue = queue.Queue()
        self._worker_thread = None
        self._connect_thread = None

        self._running = Event()
        self._cancel_connect = Event()
        self._disconnect_requested = Event()

        self._waiting_for_reply = False
        self._last_send_time = 0
        self._last_reply_time = 0

        self.state = "DISCONNECTED"

        self.on_receive = None
        self.on_state_change = None

    def connect(self, host, port):
        if self.state != "DISCONNECTED":
            return
        self._cancel_connect.clear()
        self._disconnect_requested.clear()
        self.address = (host, port)
        self._connect_thread = Thread(
            target=self._connect_worker,
            daemon=True
        )
        self._connect_thread.start()

    def disconnect(self):
        self._cancel_connect.set()
        if self.state != "CONNECTED":
            return
        self._disconnect_requested.set()

        self._set_state("DISCONNECTED")

    def send(self, data: bytes):
        self._send_queue.put(data)

    def _send(self, message, remote_addr=None):
        if self.sock:
            self.sock.sendto(message, remote_addr or self._remote_addr)

    def _connect_worker(self):
        self._set_state("CONNECTING")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.2)
            sock.connect(self.address)
        except OSError:
            self._set_state("ERROR")
            return

        start_time = time.time()
        remote_addr = None
        seq = 0
        while not self._cancel_connect.is_set():
            if time.time() - start_time > self.connect_timeout:
                sock.close()
                self._set_state("TIMEOUT")
                return
            try:
                if remote_addr:
                    sock.sendto(struct.pack('BB', *divmod(seq, 255)) + b'REQUEST', remote_addr)
                    data, addr = sock.recvfrom(self.recv_buffer)
                    print(data, addr)
                    if len(data) > 2 and seq == data[0] * 255 + data[1] and data[2:] == b'ACCEPT' and addr == remote_addr:
                        seq += 1
                        self._remote_addr = remote_addr
                        break
                else:
                    seq = 0
                    sock.sendto(struct.pack('BB', *divmod(seq,255)) + b'DISCOVER', (REMOTE_NAME, REMOTE_PORT))
                    data, addr = sock.recvfrom(self.recv_buffer)
                    print(data, addr)
                    if len(data) > 2 and seq == data[0] * 255 + data[1] and data[2:] == b'OFFER':
                        remote_addr = addr
                        seq +=1
            except socket.timeout:
                continue
            except OSError:
                sock.close()
                self._set_state("ERROR")
                return

        if self._cancel_connect.is_set():
            print("Cancelling connect")
            sock.close()
            self._set_state("DISCONNECTED")
            return

        self.sock = sock
        self._running.set()

        self._worker_thread = Thread(
            target=self._worker,
            args=(seq,),
            daemon=False
        )
        self._worker_thread.start()

        self._set_state("CONNECTED")

    def _worker(self, seq):
        try:
            while self._running.is_set():
                now = time.time()

                self._handle_receive()
                # ========== Timeout ==========
                if self._waiting_for_reply:
                    if now - self._last_send_time > self.reply_timeout:
                        if self.state == "ERROR":
                            self.disconnect()
                        self._set_state("ERROR")
                        self._waiting_for_reply = False
                        continue

                # ========== Disconnect ==========
                if self._disconnect_requested.is_set():
                    if not self._waiting_for_reply:
                        seq += 1
                        self._send_packet(seq, Command.disconnect)
                        print("Disconnect timeout")
                        break
                    time.sleep(0.01)
                    continue

                # ========== Send/Receive ==========
                if not self._waiting_for_reply:
                    try:
                        data = self._send_queue.get_nowait()
                    except queue.Empty:
                        data = None
                        for cmd in self.stat_cmds:
                            if cmd.outdated:
                                data = cmd.command
                                break
                        if now - self._last_reply_time > self.ping_interval:
                            data = data or Command.ping
                        else:
                            time.sleep(0.01)
                            continue
                    seq += 1
                    self._send_packet(seq, data)

                time.sleep(0.001)
        except Exception as e:
            self.disconnect()
            raise e
        # ========== Close Connection ==========
        print("Closing connection")
        self._running.clear()

        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass

        self._set_state("DISCONNECTED")

    def _send_packet(self, seq:int, data:bytes):
        try:
            msg = struct.pack('BB', *divmod(seq, 255)) + data
            print('Sending', msg)
            self.sock.send(msg)
            self._waiting_for_reply = True
            self._last_send_time = time.time()
        except OSError:
            self._set_state("ERROR")

    def _handle_receive(self):
        try:
            data = self.sock.recv(self.recv_buffer)
            print('Received', data)
        except socket.timeout:
            return
        except OSError:
            return

        self._waiting_for_reply = False
        self._last_reply_time = time.time()

        if data.endswith(Command.connection_timeout):
            self.disconnect()
            return
        for cmd in self.stat_cmds:
            if cmd.command == data[2:5]:
                cmd.value = data[5:]
                break
        if self.state == "ERROR":
            self._set_state("CONNECTED")

        if self.on_receive:
            self.on_receive(data)

    def _set_state(self, state):
        if self.state != state:
            self.state = state
            if self.on_state_change:
                self.on_state_change(state)

if __name__ == '__main__':
    cli = UDPClient()
    def stch(state):
        print('State changed:', state)
    cli.on_state_change = stch

    cli.connect('shittest1.local', 54321)
    try:
        while True:
            pass
    except Exception as e:
        cli.disconnect()
        raise e