# src/app.py
import tkinter as tk
from tkinter import ttk
from udp import UDPClient, Command
import bases
from football import FootballWidget
REMOTE_ADDR = ('shitbox.local', 54321)
ESTABLISH_CONNECTION_TIMEOUT = 30 # s
CONNECTION_TIMEOUT = 5 # s


# TODO:
#   - IR value
#   - TOF value
#   - search count
#   - H/V speed

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
        self.title("Shitbox - disconnected")
        self.minsize(600,400)
        self.option_add('*tearOff', False)

        self.cli = UDPClient()
        self.cli.on_state_change = self.on_state_change
        self.cli.on_receive = self.on_recv

        # ========== Shared Variables ==========
        self.connection_status = tk.StringVar(self, "DISCONNECTED", "CONN_STATUS")
        self.next_program = tk.StringVar(self, "Off", "PROGRAM")
        self.current_program = tk.StringVar(self, "Off", "CURRENT_PROGRAM")
        self.battery_status = tk.IntVar(self, 0, "BATTERY")
        self.left_wheel_power = tk.IntVar(self, 0, "LEFT_PWR")
        self.right_wheel_power = tk.IntVar(self, 0, "RIGHT_PWR")
        self.tof_value = tk.IntVar(self, 0, "TOF_VALUE")
        self.ir_value = tk.IntVar(self, 0, "IR_VALUE")


        # ========== Keybinds ==========
        self.bind('<Control-q>', self.cmd_quit)

        # ========== Widgets ==========
        # ----- Connection -----
        self.conn_widget = ConnectWidget(self)
        self.conn_widget.grid(row=0, column=0)


        # ----- Program -----
        self.program_widget = ProgramSelectWidget(self, cli=self.cli)
        self.program_widget.grid(row=1, column=0)
        self.connection_status.trace_add("write", self._on_connect)

        # ----- Football -----
        self.fb_widget = FootballWidget(self, cli=self.cli)
        self.fb_widget.grid(row=3,column=0)


        self.sensor_widget = SensorsWidget(self)
        self.sensor_widget.grid(row=4, column=0)

    def _on_connect(self, *args):
        self.program_widget.set_active(self.connection_status.get() == 'CONNECTED')

    def cmd_quit(self, event=None):
        self.quit()

    def quit(self):
        self.cli.disconnect()
        self.after(50, super().quit)

    def cmd_set_program(self, event=None):
        self.set_program()

    def on_state_change(self, state):
        self.connection_status.set(state)
        self.update_widgets()

    def on_recv(self, data):
        cmd = data[2:5]
        data = data[5:]
        self.battery_status.set(self.cli.battery.value or 0)
        if cmd == self.program_widget.cmd_name:
            n = [prg for prg, val in self.program_widget.programs.items() if val == data][0]
            self.current_program.set(n)
        self.update_widgets()

    def update_widgets(self):
        self.conn_widget.update_fmt()
        self.fb_widget.update_state(self.connection_status.get() == 'CONNECTED')

    def connect(self):
        self.cli.connect(*REMOTE_ADDR)

    def disconnect(self):
        self.cli.disconnect()

class ConnectWidget(tk.Frame):
    # TODO: Remove - Depricated
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

class ProgramSelectWidget(tk.Frame):
    cmd_name = b'PRG'
    programs = {'Off': b'NN', 'Football': b'FB', 'Sumo': b'SU', 'Wall Follow': b'WF'}
    def __init__(self, master:App, cli:UDPClient, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master:App = master
        self.cli = cli
        self.current_program = self.master.current_program
        self.next_program = self.master.next_program
        self._active = False

        self.prg_label = ttk.Label(self, name='prg_header', textvariable=self.current_program, font=('Arial', 16))
        self.prg_label.grid(row=0, column=0, columnspan=2)

        self.dropdown = ttk.Combobox(
            self,
            validate='all',
            validatecommand=self.cmd_prg_select,
            textvariable=self.next_program,
            values=list(self.programs.keys()),
            state='disabled',
        )
        self.dropdown.grid(row=1, column=0)

        self.btn_confirm = ttk.Button(self, text='Confirm', command=self.cmd_confirm, state='disabled')
        self.btn_confirm.grid(row=1, column=1)
        self.activate() # DEBUG

    def set_program(self, prg:bytes):
        self.current_program.set([nam for nam, val in self.programs.items() if val == prg][0])

    def cmd_confirm(self, event=None):
        self.cli.queue_command_nowait(self.cmd_name)

    def cmd_prg_select(self, *args):
        if self.is_active:
            self.btn_confirm['state'] = 'disabled' if self.current_program.get() == self.next_program.get() else 'normal'
        else:
            self.btn_confirm['state'] = 'disabled'
        return True

    @property
    def is_active(self):
        return self._active

    def activate(self):
        self._active = True
        self.dropdown.config(state='normal')
        self.cmd_prg_select()

    def deactivate(self):
        self.dropdown.config(state='disabled')
        self.cmd_prg_select()

    def set_active(self, state):
        if state:
            self.activate()
        else:
            self.deactivate()


    @property
    def curr_program(self):
        return self.current_program.get()

    @curr_program.setter
    def curr_program(self, value:str):
        self.current_program.set(value)

    @property
    def nxt_program(self):
        return self.next_program.get()

    @nxt_program.setter
    def nxt_program(self, value):
        self.next_program.set(value)

class WheelScale(ttk.Frame):
    def __init__(self, master, text:str, variable:tk.IntVar, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.variable = variable
        self.text_var = tk.StringVar(self, '0')
        self.variable.trace_add('write', self._update_var)

        self.header = ttk.Label(self, text=text)
        self.header.grid(row=0, column=0)

        self.scale = ttk.Progressbar(self, orient="vertical", variable=self.variable)
        self.scale.grid(row=1, column=0)

        self.label = ttk.Label(self, textvariable=self.text_var)
        self.label.grid(row=2, column=0)

    def _update_var(self):
        self.text_var.set(str(self.variable.get()))

class SensorsWidget(tk.Frame):
    def __init__(self, master:App, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master:App = master
        self.left_speed_var = master.left_wheel_power
        self.right_speed_var = master.right_wheel_power
        self.tof_var = master.tof_value
        self.tof_text = tk.StringVar(self, '- mm')
        self.tof_var.trace_add("write", lambda: self.tof_text.set((str(self.tof_var.get())if self.master.connection_status.get() == 'CONNECTED' else '-') + ' mm'))
        self.ir_var = master.ir_value
        self.ir_text = tk.StringVar(self, '-')

        self.left_wheel_scale = WheelScale(self, text='L', variable=self.left_speed_var)
        self.left_wheel_scale.grid(row=0, column=0)
        self.right_wheel_scale = WheelScale(self, text='R', variable=self.right_speed_var)
        self.right_wheel_scale.grid(row=0, column=1)


        self.tof_scale = ttk.Progressbar(self, orient="horizontal", variable=self.tof_var)


if __name__ == '__main__':
    main()