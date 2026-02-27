# src/app.py
import tkinter as tk
from tkinter import ttk
from udp import UDPClient, Command
import struct

class Program:
    football = b'FB'
    sumo = b'SU'
    wall_follow = b'WF'
    idle = b'NN'

REMOTE_ADDR = ('shitbox.local', 54321)
ESTABLISH_CONNECTION_TIMEOUT = 30 # s
CONNECTION_TIMEOUT = 5 # s

def main():
    app = App()
    try:
        app.mainloop()
    except Exception as e:
        app.quit()
        raise e

class App(tk.Tk):
    _seq = 0
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

        self.cli = UDPClient()
        self.cli.on_state_change = self.on_state_change
        self.cli.on_receive = self.on_recv

        # ========== Shared Variables ==========
        self.connection_status = tk.StringVar(self, "DISCONNECTED", "CONN_STATUS")
        self.program = tk.StringVar(self, "Off", "PROGRAM")
        self.current_program = tk.StringVar(self, "Off", "CURRENT_PROGRAM")
        self.battery_status = tk.IntVar(self, 0, "BATTERY")

        # ========== Keybinds ==========
        self.bind('<Control-q>', self.cmd_quit)

        # ========== Widgets ==========
        # ----- Connection -----
        self.conn_widget = ConnectWidget(self)
        self.conn_widget.grid(row=0, column=0)


        # ----- Program -----
        self.prg_label = ttk.Label(self, textvariable=self.current_program)
        self.prg_label.grid(row=1,column=0, columnspan=2)
        self.prg_drp_dwn = ttk.Combobox(
            values=['Off', 'Football', 'Sumo', 'Wall follow'],
            textvariable=self.program,
            state='normal'
        )
        self.prg_drp_dwn.bind('<Return>', self.cmd_set_program)
        self.prg_drp_dwn.grid(row=2, column=0)
        self.prg_confirm = ttk.Button(text="Update program", state='normal', command=self.cmd_set_program)
        self.prg_confirm.grid(row=2, column=1)

        # ----- Football -----
        self.fb_widget = FootballWidget(self)
        self.fb_widget.grid(row=3,column=0)

    def cmd_quit(self, event=None):
        self.quit()

    def quit(self):
        self.cli.disconnect()
        self.after(50, super().quit)

    def cmd_set_program(self, event=None):
        self.set_program()

    def on_state_change(self, state):
        self.connection_status.set(state)
        self.after(5, self.update_widgets)

    def on_recv(self, data):
        cmd = data[2:5]
        data = data[5:]
        print("ON Received", cmd, data)
        self.battery_status.set(self.cli.battery.value or 0)
        if cmd == Command.program:
            match data:
                case Program.idle:
                    self.current_program.set('Off')
                case Program.wall_follow:
                    self.current_program.set('Wall Follow')
                case Program.sumo:
                    self.current_program.set('Sumo')
                case Program.football:
                    self.current_program.set('Football')
        self.update_widgets()

    def update_widgets(self):
        self.conn_widget.update_fmt()
        if self.connection_status.get() == 'CONNECTED':
            self.prg_drp_dwn.config(state='normal')
            self.prg_confirm.config(state='normal')
        else:
            self.prg_drp_dwn.config(state='disabled')
            self.prg_confirm.config(state='disabled')
        self.fb_widget.update_fmt()

    def connect(self):
        self.cli.connect(*REMOTE_ADDR)

    def disconnect(self):
        self.cli.disconnect()

    def set_program(self):
        cmds = {
            'Football': b'FB',
            'Off': b'NN',
            'Sumo': b'SU',
            'Wall Follow': b'WF'
        }
        if self.program.get() in cmds:
            cmd = cmds[self.program.get()]
        else:
            cmd = cmds['Off']
        self.cli.send(Command.program + cmd)

class ConnectWidget(tk.Frame):
    def __init__(self, master:App, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master:App = master
        #self.master.connection_status.trace_add("write", self.update_fmt)
        # ========== UI Elements ==========
        ttk.Label(self, name='conn_header', text='Status').grid(row=0, column=0, columnspan=3)
        self.stat_label = ttk.Label(self, name="conn_label", foreground='crimson', textvariable=master.connection_status)
        self.stat_label.grid(row=1, column=0)
        self.conn_button = ttk.Button(self, name="conn_button", text='Connect', command=self.cmd_connect)
        self.conn_button.grid(row=1, column=1, padx=20)
        self.batt_stat = ttk.Progressbar(self, maximum=255, variable=self.master.battery_status)
        self.batt_stat.grid(row=1, column=2)

    def update_fmt(self, *_):
        match self.master.connection_status.get():
            case 'CONNECTED':
                self.fmt_connected()
            case 'DISCONNECTED':
                self.fmt_disconnected()
            case 'CONNECTING':
                self.fmt_connecting()

    def fmt_connected(self):
        self.stat_label.config(foreground='darkgreen')
        self.conn_button.config(text='Disconnect', command=self.cmd_disconnect)

    def fmt_disconnected(self):
        self.stat_label.config(foreground='Crimson')
        self.conn_button.config(text='Connect', command=self.cmd_connect)

    def fmt_connecting(self):
        self.stat_label.config(foreground='black')
        self.conn_button.config(text='Abort', command=self.cmd_disconnect)

    def cmd_connect(self):
        self.master.connect()

    def cmd_disconnect(self):
        self.master.disconnect()

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

        self.fmt_disabled()

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

    def fmt_normal(self):
        self.fwd['state'] = 'normal'
        self.bck['state'] = 'normal'
        self.lef['state'] = 'normal'
        self.rig['state'] = 'normal'
        self.stp['state'] = 'normal'
        self.spd_adjust['state'] = 'normal'

    def fmt_disabled(self):
        self.fwd['state'] = 'disabled'
        self.bck['state'] = 'disabled'
        self.lef['state'] = 'disabled'
        self.rig['state'] = 'disabled'
        self.stp['state'] = 'disabled'
        self.spd_adjust['state'] = 'disabled'

    def update_fmt(self):
        print("Updating football fmt", self.master.connection_status.get(), self.master.current_program.get())
        if self.master.connection_status.get() == "CONNECTED" and self.master.current_program.get() == "Football":
            self.fmt_normal()
        else:
            self.fmt_disabled()

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
        self.on_key_press(self.DummyPress('x'))

if __name__ == "__main__":
    main()
