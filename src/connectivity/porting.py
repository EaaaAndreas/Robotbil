# src/connectivity/porting.py
import usocket as socket
import ustruct
from net_setup import get_ip
from time import ticks_ms, ticks_diff


_used_ports = set()

battery_status = 0 # TODO: Placeholder
program = 0 # TODO: Placeholder


def _get_unused_port(min_:int=50001) -> int:
    if len(_used_ports):
        for port in _used_ports:
            if port >= min_ and port + 1 not in _used_ports:
                return port + 1
    return min_

class UDPSocket:
    _ip:str = None
    _port = 0
    _que = {}
    _pending = set()
    _temp_remote_addr = None
    def __init__(self, ip:str|None=None, port:int=0, connection_timeout:int=5000, callbacks:dict=None):
        """
        A class for sending and receiving messages to a connected remote host.
        This class will automatically connect to a host, if the host follows the connection protocol. Then, only this
        remote host is allowed to communicate with the socket. The property `allow_movement` returns True if the
        instance is connected and the time since the last message is not greater than the connection_timeout timer.
        :param ip: The IPv4-address of the socket. See `UDPSocket.set_ip`
        :type ip: str|None
        :param port: The port of the socket. See `UDPSocket.set_port`
        :type port: int
        :param connection_timeout: The time (ms) since last message before the module disallows movement.
        :type connection_timeout: int
        :param callbacks: Callbacks to call, when commands have come in
        :type callbacks: dict
        """
        self.set_ip(ip)
        self.set_port(port)
        self._bound = False
        self._callbacks = {}
        self.add_callback(callbacks)
        self._remote_addr = (None, None)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._timeout_ms = connection_timeout
        self._connection_timer = ticks_ms()

    def add_callback(self, callbacks:dict[str, object]) -> None:
        """
        Add one or more callbacks to the instance. This must be a dict[cmd, callback]. When the instance receives a
        command, the callback, belonging to this command will be called.
        :param callbacks: A dictionary with command and callback.
        :type callbacks: dict[str, object]
        :return: None
        """
        self._callbacks.update(callbacks)

    def remove_callback(self, key:str) -> None:
        """
        Remove a callback from the instance
        :param key: The command, bound to the callback
        :type key: str
        :return: None
        """
        if key in self._callbacks:
            self._callbacks.pop(key)
        else:
            print(f"[UDP] Tried to remove callback '{key}'. But it was not found.")

    def que_reply(self, seq, message:str=None) -> None:
        """
        Add a reply to the que. To get sent, next time UDPSocket.send_que() is called.
        :param seq: The sequence number belonging to the reply
        :type seq: int
        :param message: The message to send
        :type message: str
        :return: None
        """
        self._que[seq] = message.encode('ascii') if message else b'0'

    def _init(self, rebind:bool=False) -> None:
        """
        Prepare the class for sending/receiving.
        :param rebind: If True, the socket will be restarted (useful when changing port).
        :type rebind: bool
        :return: None
        """
        if self._bound:
            if rebind:
                self.close_socket()
                self.bind()
        else:
            self.bind()
        self.sock.setblocking(False)

    def close_socket(self) -> None:
        """
        Close the socket of the instance.
        :return: None
        """
        if self._bound:
            self.sock.close()
            self._bound = False

    def _connect(self, data:bytes, addr:tuple) -> None:
        # Establish a connection to a remote host
        if data[1:] == b'DISCOVER':
            self._temp_remote_addr = addr
            self.que_reply(data[0], 'OFFER')

        elif data[1:] == b'REQUEST' and self._temp_remote_addr:
            if addr == self._temp_remote_addr:
                self.que_reply(data[0], 'ACCEPT')
                self._remote_addr = addr
                self._temp_remote_addr = None

    def _handle_message(self, data:bytes) -> None:
        # Handle a message, calling any callbacks and resetting timeout timer.
        if data[1] in self._callbacks.keys():
            if self._que[data[0]]:
                print(f"[UDP] Tried to add sequence '{data[0]}' to que. But it already exists.")
            self._callbacks[data[1]](data[0], data[2])
            self._connection_timer = ticks_ms()
        else:
            self._que[data[0]] = ''

    def recvfrom(self, bufsize:int=1024):
        """
        Generator function. Receives and yields all messages, like socket.socket.recvfrom(), handling error, when no
        message can be fetched.
        :param bufsize: The buffer size of the message to receive. (See `socket.socket.recvfrom`)
        :type bufsize: int
        :return: Generates all pending messages. Returns None when none are pending.
        :rtype: tuple[bytes, tuple[int,str]] | None
        """
        try:
            yield self.sock.recvfrom(bufsize)
        except OSError as e:
            print(e)
            return None

    def listen_task(self) -> None:
        """
        A task to add to main loop. This task makes sure, all pending messages are received and handled.
        :return: None
        """
        for data, addr in self.recvfrom():
            if self.connected:
                if self._remote_addr == addr:
                    self._handle_message(data)
            else:
                self._connect(data, addr)

    def send_que(self) -> None:
        """
        Sends all messages in the que.
        :return: None
        """
        for seq in self._pending:
            # [SEQUENCE][BATTERY][PROGRAM][MESSAGE]
            self.send(ustruct.pack('xBBB', seq, battery_status, program) + bytes(self._que[seq]))

    def send(self, message:bytes, addr:tuple[str,int]=None) -> None:
        """
        Send a message to the given address, or the connected remote host, if addr is None
        :param message: The message to be sent
        :type message: bytes
        :param addr: The address of the receiver. If None, the message will be sent to the connected remote host.
        :type addr: tuple[str, int]|None
        :return: None
        """
        if addr is None and self._remote_addr is None:
            print(f"[UDP] Not bound to any host. Cannot send message '{message}'. No address given.")
        else:
            self.sock.sendto(message, self._remote_addr if addr is None else addr)

    def set_ip(self, ip:str|None=None) -> None:
        """
        Set the ip of the local socket
        :param ip: IPv4 address. This is generated automatically if None.
        :type ip: str|None
        :return: None
        """
        self._ip = get_ip() if ip is None else ip
        if self._bound:
            self.sock.close()
            self.sock.bind(self.addr)

    def set_port(self, port:int=0, use_next=False) -> None:
        """
        Set the port number of the local socket.
        :param port: The port number. One is automatically found if `0`
        :type port: int
        :param use_next: If True, the function will automatically find the next available port number. Else, an
            exception is raised, if the port is in use.
        :type use_next: bool
        :return: None
        """
        if port == 0:
            if self._port == 0:
                self._port = _get_unused_port()
        elif port not in _used_ports:
            _used_ports.remove(self._port)
            self._port = port
        elif use_next:
            _used_ports.remove(self._port)
            self._port = _get_unused_port(port)
        else:
            raise Exception(f"Port {port} already in use.")
        _used_ports.add(self._port)
        if self._bound:
            self.close_socket()
            self.bind()

    def set_connection_timeout(self, timeout_ms:int) -> None:
        """
        Set the time it takes since the last received command before the module times out.
        :param timeout_ms: Timeout in ms
        :type timeout_ms: int
        :return: None
        """
        self._timeout_ms = timeout_ms

    def bind(self) -> None:
        """
        Bind this socket to it's port and address. If no port or address has been set. These will be generated.
        :return: None
        """
        if not self._bound:
            if not self.port or not self.ip_addr:
                self.addr = (self.ip_addr, self.port)
            self.sock.bind(self.addr)
            self._bound = True

    @property
    def ip_addr(self) -> str:
        return self._ip
    @property
    def port(self) -> int:
        return self._port
    @property
    def addr(self) -> tuple[str, int]:
        return self.ip_addr, self.port
    @addr.setter
    def addr(self, addr:tuple[str, int]):
        self.set_ip(addr[0])
        self.set_port(addr[1])
    @property
    def connected(self):
        return not self._remote_addr == (None, None)
    @property
    def allow_movement(self) -> bool:
        return self.connected and self._connection_timer < self._timeout_ms

    def __del__(self, *args):
        self.close_socket()
        return args