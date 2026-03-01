# src/udp.py
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
    football = b'FBC'


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

#REMOTE_NAME = 'shitbox.local'
#REMOTE_PORT = 54321

class CmdQueue(queue.Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def remove_command(self, command:bytes):
        if self.not_empty:
            for c in self.queue:
                if c[0] == command:
                    self.queue.remove(c)

    def put_cmd(self, cmd:bytes, data:bytes= b'', remove_old=False, **kwargs):
        if remove_old:
            for c in self.queue:
                if c.startswith(cmd):
                    self.queue.remove(c)
        self.put(cmd + data, **kwargs)

    def put_cmd_nowait(self, cmd:bytes, data:bytes= b'', remove_old=False):
        print(cmd, data)
        if remove_old:
            for c in self.queue:
                if c.startswith(cmd):
                    self.queue.remove(c)
        self.put_nowait(cmd + data)

class UDPClient:
    def __init__(self, ping_interval=1.0, reply_timeout=5.0, connect_timeout=10.0, recv_buffer=2048, local_addr=None):
        self.ping_interval = ping_interval
        self.reply_timeout = reply_timeout
        self.connect_timeout = connect_timeout
        self.recv_buffer = recv_buffer

        self.battery = RemoteStatus(Command.battery, 5, 'B')

        self.stat_cmds = [self.battery]

        self.sock = None
        self.local_addr = local_addr or ('0.0.0.0', 0)
        self.remote_addr = None

        self._send_queue = CmdQueue()
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
        self._running.clear()
        self._cancel_connect.clear()
        self._disconnect_requested.clear()
        self.remote_addr = (host, port)
        self._connect_thread = Thread(
            target=self._connect_worker,
            daemon=False
        )
        self._connect_thread.start()

    def disconnect(self):
        self._cancel_connect.set()
        self._disconnect_requested.set()
        self._running.clear()

        # Wait for connect thread
        if self._connect_thread and self._connect_thread.is_alive():
            self._connect_thread.join(timeout=2)

        # Wait for worker thread
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2)

        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass

        self._set_state("DISCONNECTED")

    def queue_command(self, command:str|bytes, data:str|bytes=b'', remove_old=False, **kwargs):
        if isinstance(command, str):
            command = command.encode('ascii')
        if isinstance(data, str):
            data = data.encode('ascii')
        self._send_queue.put_cmd(command, data, remove_old=remove_old, **kwargs)

    def queue_command_nowait(self, command:str|bytes, data:str|bytes=b'', remove_old:bool=False):
        if isinstance(command, str):
            command = command.encode('ascii')
        if isinstance(data, str):
            data = data.encode('ascii')
        self._send_queue.put_cmd_nowait(command, data, remove_old=remove_old)

    def clear_command(self, command:str|bytes=b''):
        if isinstance(command, str):
            command = command.encode('ascii')
        self._send_queue.remove_command(command)

    def _send(self, message, remote_addr=None):
        if self.sock:
            self.sock.sendto(message, remote_addr or self._remote_addr)

    def _connect_worker(self):
        print("[UDP-connect] Establishing connection")
        self._set_state("CONNECTING")
        try:
            print("[UDP-connect] Opening socket")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.2)
            sock.bind(self.local_addr)
        except OSError as e:
            self._set_state("ERROR")
            print("[UDP-connect] An error occured while opening socket:", e)
            return

        start_time = time.time()
        offer_made = False
        seq = 0
        print("[UDP-connect] Starting connection sequence")
        while not self._cancel_connect.is_set():
            if time.time() - start_time > self.connect_timeout:
                sock.close()
                self._set_state("TIMEOUT")
                print("[UDP-connect] Connection attempt timed out")
                return
            try:
                if offer_made:
                    sock.sendto(struct.pack('BB', *divmod(seq, 255)) + b'REQUEST', self.remote_addr)
                    data = sock.recv(self.recv_buffer)
                    print("[UDP-connect] (Offer made) Received", data)
                    if len(data) > 2 and seq == data[0] * 255 + data[1] and data[2:] == b'ACCEPT':
                        seq += 1
                        print("[UDP-connect] Received connection accept")
                        break
                else:
                    seq = 0
                    sock.sendto(struct.pack('BB', *divmod(seq,255)) + b'DISCOVER', self.remote_addr)
                    data, addr = sock.recvfrom(self.recv_buffer)
                    print("[UDP-connect] (No offer) Received", data, addr)
                    if len(data) > 2 and seq == data[0] * 255 + data[1] and data[2:] == b'OFFER':
                        sock.connect(self.remote_addr)
                        seq +=1
                        offer_made = True
                        print("[UDP-connect] Received connection accept")
            except socket.timeout:
                continue
            except OSError as e:
                sock.close()
                self._set_state("ERROR")
                print("[UDP-connect] An error occurred while connecting:", e)
                return

        if self._cancel_connect.is_set():
            print("[UDP-connect] Connection attempt was manually canceled")
            sock.close()
            self._set_state("DISCONNECTED")
            return

        print("[UDP-connect] Connection established successfully. Starting main thread")
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
        print("[UDP] Main thead started")
        try:
            while self._running.is_set():
                now = time.time()

                self._handle_receive()
                # ========== Timeout ==========
                if self._waiting_for_reply:
                    if now - self._last_send_time > self.reply_timeout:
                        print("[UDP] Connection timed out")
                        if self.state == "ERROR":
                            print("[UDP] Closing main thread")
                            self.disconnect()
                        else:
                            print("[UDP] Making one more attempt")
                        self._set_state("ERROR")
                        self._waiting_for_reply = False
                        continue

                # ========== Disconnect ==========
                if self._disconnect_requested.is_set():
                    print("[UDP] Disconnect requested")
                    if not self._waiting_for_reply:
                        print("[UDP] Sending disconnect message")
                        seq += 1
                        self._send_packet(seq, Command.disconnect)
                    break

                # ========== Send/Receive ==========
                if not self._waiting_for_reply:
                    try:
                        d = self._send_queue.get_nowait()
                        data = d
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
        finally:
            # ========== Close Connection ==========
            print("[UDP] Closing main thread")
            self._running.clear()

            if self.sock:
                try:
                    self.sock.close()
                except OSError as e:
                    print("[UDP] An error occurred while closing socket:", e)

            self._set_state("DISCONNECTED")

    def _send_packet(self, seq:int, data:bytes):
        try:
            msg = struct.pack('BB', *divmod(seq, 255)) + data
            print('[UDP-SEND]', msg)
            self.sock.send(msg)
            self._waiting_for_reply = True
            self._last_send_time = time.time()
        except OSError:
            self._set_state("ERROR")

    def _handle_receive(self):
        try:
            data = self.sock.recv(self.recv_buffer)
            print('[UDP-RECEIVE]', data)
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
        print("[UDP-STATE] Set", state)
        if self.state != state:
            self.state = state
            print("[UDP-STATE] Changed state to", self.state)
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