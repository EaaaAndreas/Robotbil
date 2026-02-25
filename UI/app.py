# src/app.py
import tkinter as tk
from tkinter import ttk
import socket
import struct
from time import time, sleep
from enum import Enum, auto

class Status(Enum):
    CONNECTED = auto()
    CONNECTING = auto()
    DISCONNECTED = auto()
    CONNECTION_ERROR = auto()

class Program:
    football = b'FB'
    sumo = b'SU'
    wall_follow = b'WF'
    idle = b'NN'


REMOTE_ADDR = ('shittest1.local', 54321)
ESTABLISH_CONNECTION_TIMEOUT = 30 # s
CONNECTION_TIMEOUT = 5 # s

def main():
    app = App()
    app.mainloop()

class App(tk.Tk):
    _seq = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _remote_addr = REMOTE_ADDR[0]
    _remote_port = REMOTE_ADDR[1]
    _timeout_timer = 0
    def __init__(self):
        # ========== Setup app ==========
        super().__init__()
        # self.sock = UDPSocket()
        self.title("Shitbox - disconnected")
        self.minsize(600,400)
        self.option_add('*tearOff', False)

        self.sock.settimeout(5)
        self.sock.bind(('0.0.0.0', 0))
        # ========== Shared Variables ==========
        self.connection_status = tk.StringVar(self, Status.DISCONNECTED, "CONN_STATUS")
        #self.connected = tk.BooleanVar(self, False, "CONNECTED")
        self.battery_status = tk.IntVar(self, 0, "BATTERY")
        self.program = tk.StringVar(self, 'Off', "PROGRAM")
        self.next_program = tk.StringVar(self, 'Off', 'NEXTPRG')

        # ========== Keybinds ==========
        self.bind('<Control-q>', self.cmd_quit)
        self.bind('<Control-w>', self.stop_slave)
        self._ast = self.connection_status.trace_add("write", self._autostart_ping)

        self.conn_widget = ConnectWidget(self)
        self.conn_widget.grid(row=0, column=0)
        self.connection_status.trace_add('write', self.conn_widget.update_fmt)

        #self.conn_button = ttk.Button(self, text='Connect', command=self.connect)
        #self.conn_button.grid(row=0, column=2, padx=20)
        #self.conn_battery = ttk.Progressbar(self, maximum=255, variable=self.battery_status)
        #)self.conn_battery.grid(row=0, column=3, padx=20)

        self.prg_label = ttk.Label(self, textvariable=self.program)
        self.prg_label.grid(row=1,column=0)
        self.fb_widget = FootballWidget(self)
        self.fb_widget.grid(row=2,column=0)

        self.prg_drp_dwn = ttk.Combobox(
            values=['Off', 'Football', 'Sumo', 'Wallfollow'],
            #validate='all',
            #validatecommand=self.cmd_selected_program,
            textvariable=self.next_program,
            state='normal'
        )
        self.prg_drp_dwn.grid(row=1, column=1)
        self.prg_confirm = ttk.Button(text="Update program", state='normal', command=self.set_program)
        self.prg_confirm.grid(row=1, column=2)


        #self.fb_widget = FootballWidget(self)
        #self.fb_widget.grid(row=2, column=0, columnspan=4)

    def set_conn(self, val:bool):
        self.connected.set(val)
        idx = int(val)
        state = ['disabled', 'normal'][idx]
        self.conn_status.config(text=['Disconnected', 'Connected'][idx], foreground=['crimson', 'darkgreen'][idx])
        self.conn_button.config(text=['Connect', 'Disconnect'][idx], command=[self.cmd_connect, self.cmd_disconnect][idx])
        self.prg_drp_dwn.config(state=state)
        self.prg_confirm.config(state=state)

    def cmd_quit(self, event=None):
        self.disconnect()
        self.sock.close()
        self.quit()

    def cmd_selected_program(self, event=None):
        if self.next_program.get() != self.program.get():
            self.prg_confirm['state'] = 'disabled'
        else:
            self.prg_confirm['state'] = 'normal'
        return True

    def _sendto(self, message:bytes, remote_addr=None):
        if isinstance(message, str):
            message = message.encode('ascii')
        seq = self._seq
        print(f"[UDP] Sending '{struct.pack('BB', *divmod(seq, 255)) + message}' to {remote_addr or self.remote_addr}")
        self.sock.sendto(struct.pack('BB', *divmod(seq,255)) + message, remote_addr or self.remote_addr)
        self._seq += 1
        return seq

    def sendto(self, message:bytes):
        print("Sending", message, self.connection_status.get())
        if self.connection_status.get() == Status.CONNECTED:
            return self._sendto(message)
        raise IOError(f"Couldn't send message. Not connected.")

    def _recv(self, remote_addr=None):
        try:
            message = self.sock.recvfrom(1024)
            if message is not None:
                print(f"[UDP] Received '{message}'")
                if len(message[0]) > 2:
                    data, addr = message
                    seq = data[0] * 255 + data[1]
                    data = data[2:]
                    if seq < self._seq:
                        if self.connection_status.get() != Status.CONNECTED:
                            return seq, data, addr
                        elif addr == (remote_addr or self.remote_addr):
                            self._timeout_timer = time()
                            return seq, data
        except BlockingIOError:
            pass
        return None
    
    @property
    def conn_status(self):
        return self.connection_status.get()
    
    @conn_status.setter
    def conn_status(self, value):
        self.connection_status.set(value)
    
    
    def connect(self):
        if self.is_connected():
            raise ConnectionAbortedError(f"Already connected")
        print('[UDP-connect] Establishing connection')
        remote_addr = None
        self.connection_status.set(Status.CONNECTING)
        print('[UDP-connect] Connecting', self.connection_status.get(), self.is_connected())
        seq = self._sendto(b'DISCOVER', REMOTE_ADDR)
        t0 = time()
        while time() - t0 < ESTABLISH_CONNECTION_TIMEOUT:
            message = self._recv(remote_addr)
            if message is not None:
                print(f"[UDP-connect] received message '{message}'")
                rseq, data, addr = message
                if rseq == seq:
                    print(rseq, data, addr, remote_addr)
                    if data == b'OFFER':
                        print('[UDP-connect] Identified offer. Sending request')
                        seq = self._sendto(b'REQUEST')
                        remote_addr = addr
                    elif data == b'ACCEPT' and remote_addr == addr:
                        self.connection_status.set(Status.CONNECTED)
                        print(f"[UDP-connect] Connected to '{self.remote_addr}'", self.connection_status.get(), self.is_connected())
                        return
                else:
                    print(f"[UDP-connect] Unmatched sequence number '{seq}'")
        self.connection_status.set(Status.CONNECTION_ERROR)
        raise TimeoutError(f"Took too long to connect")

    def _ping(self):
        self.sendto(b'PIN')
        print(self.recv())

    def _ping_loop(self):
        with self._communicating:
            while self._pinging:
                self._ping()
                sleep(1)

    def _autostart_ping(self, *_):
        if self.is_connected():
            self.after(10, self.start_ping_loop)
            self.connection_status.trace_remove('write', self._ast)

    def stop_ping_loop(self):
        if self._pinging:
            self._pinging = False
        self._ast = self.connection_status.trace_add('write', self._autostart_ping)

    def disconnect(self):
        pass

    def set_program(self):
        match self.next_program.get():
            case 'Football':
                self.program.set('Football')
                prg = Program.football
            case 'Sumo':
                self.program.set('Sumo')
                prg = Program.sumo
            case 'Wall Follow':
                self.program.set('Wall Follow')
                prg = Program.wall_follow
            case _:
                self.program.set('Off')
                prg = Program.idle
        self._sendto(b'PRG' + prg)

    def stop_slave(self, event=None):
        pass

    @property
    def remote_name(self):
        return self._remote_addr

    @property
    def remote_port(self):
        return self._remote_port

    @property
    def remote_addr(self):
        return self.remote_name, self.remote_port

    def is_connected(self):
        return self.connection_status.get() == Status.CONNECTED

class ConnectWidget(tk.Frame):
    def __init__(self, master:App, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master:App = master
        #self.master.connection_status.trace_add("write", self.update_fmt)
        # ========== UI Elements ==========
        ttk.Label(self, name='conn_header', text='Status').grid(row=0, column=0, columnspan=3)
        self.stat_label = ttk.Label(self, name="conn_label", text='Disconnected', foreground='crimson')
        self.stat_label.grid(row=1, column=0)
        self.conn_button = ttk.Button(self, name="conn_button", text='Connect', command=self.cmd_connect)
        self.conn_button.grid(row=1, column=1, padx=20)
        self.batt_stat = ttk.Progressbar(self, maximum=255, variable=self.master.battery_status)
        self.batt_stat.grid(row=1, column=2)

    def update_fmt(self, *_):
        match self.master.connection_status.get():
            case Status.CONNECTED:
                self.fmt_connected()
            case Status.CONNECTING:
                self.fmt_connecting()
            case _:
                self.fmt_disconnected()

    def fmt_connected(self):
        self.stat_label.config(text='Connected', foreground='darkgreen')
        self.conn_button.config(text='Disconnect', command=self.cmd_disconnect)

    def fmt_disconnected(self):
        self.stat_label.config(text='Disconnected', foreground='Crimson')
        self.conn_button.config(text='Connect', command=self.cmd_connect)

    def fmt_connecting(self):
        self.stat_label.config(text='Connecting...', foreground='black')
        self.conn_button.config(text='Abort', command=self.cmd_abort_connection)

    def cmd_connect(self):
        self.master.connect()


    def cmd_abort(self):
        self.conn_button['state'] = 'disabled'
        self.stat_label['text'] = 'aborting'
        pass

    def cmd_disconnect(self):
        pass

    def cmd_abort_connection(self):
        pass

class FootballWidget(tk.Frame):
    def __init__(self, master:App, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master:App = master
        self.pressed = set()
        self.direction = tk.StringVar(self, "X", "FB_DIR")
        self.speed = tk.IntVar(self, 0, "FB_SPD")

        self.fwd = ttk.Button(self, text="↑", command=self.cmd_fwd)
        self.fwd.grid(row=0, column=1)
        self.bck = ttk.Button(self, text="↓", command=self.cmd_bck)
        self.bck.grid(row=2, column=1)
        self.lef = ttk.Button(self, text="←", command=self.cmd_lef)
        self.lef.grid(row=1, column=0)
        self.rig = ttk.Button(self, text="→", command=self.cmd_rig)
        self.rig.grid(row=1,column=2)
        self.stp = ttk.Button(self, text="STOP", command=self.cmd_stop)
        self.stp.grid(row=1, column=1)

        master.bind("<KeyPress>", self.on_key_press)
        master.bind("<KeyRelease>", self.on_key_release)

        self.spd_adjust = ttk.Scale(self,orient='vertical', to=255, variable=self.speed)
        self.spd_adjust.grid(row=0, column=4, rowspan=3, padx=20)

    def update_buttons(self):
        self.fwd['state'] = 'active' if 'w' in self.pressed else 'normal'
        self.bck['state'] = 'active' if 's' in self.pressed else 'normal'
        self.lef['state'] = 'active' if 'a' in self.pressed else 'normal'
        self.rig['state'] = 'active' if 'd' in self.pressed else 'normal'
        self.stp['state'] = 'active' if 'x' in self.pressed else 'normal'

    def on_key_press(self, event):
        key = event.keysym.lower()
        match key:
            case 'w' | 'up':
                if 's' not in self.pressed:
                    self.pressed.discard('x')
                    self.pressed.add('w')
            case 's' | 'down':
                if 'w' not in self.pressed:
                    self.pressed.discard('x')
                    self.pressed.add('s')
            case 'a' | 'left':
                if 'd' not in self.pressed:
                    self.pressed.discard('x')
                    self.pressed.add('a')
            case 'd' | 'right':
                if 'a' not in self.pressed:
                    self.pressed.discard('x')
                    self.pressed.add('d')
        self.update_buttons()
        self.send_command()

    def send_command(self):
        cmd = b'FBC'
        if 'w' in self.pressed:
            if 'a' in self.pressed:
                cmd += b'Q'
            elif 'd' in self.pressed:
                cmd += b'E'
            else:
                cmd += b'W'
        elif 's' in self.pressed:
            if 'a' in self.pressed:
                cmd += b'Z'
            elif 'd' in self.pressed:
                cmd += b'C'
            else:
                cmd += b'S'
        else:
            cmd += b'X'
        cmd += struct.pack('B', self.speed.get())
        self.master._sendto(cmd)

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key == 'up':
            key = 'w'
        elif key == 'down':
            key = 's'
        elif key == 'left':
            key = 'a'
        elif key == 'right':
            key = 'd'
        self.pressed.discard(key)
        if len(self.pressed) == 0:
            self.pressed.add('x')
        self.update_buttons()

    class DummyPress:
        def __init__(self, key:str):
            self.key = key
        @property
        def keysym(self):
            return self.key

    def cmd_fwd(self):
        self.on_key_press(self.DummyPress('w'))

    def cmd_bck(self):
        pass
    def cmd_rig(self):
        pass
    def cmd_lef(self):
        pass
    def cmd_stop(self):
        pass

if __name__ == "__main__":
    main()
