import tkinter as tk
from tkinter import ttk
import struct
from udp import UDPClient

BUTTON_OPPOSITES = {
    'N': 'S',
    'S': 'N',
    'E': 'W',
    'W': 'E'
}

def parse_button(button:str) -> str | None:
    button = button.lower()
    if button in ('w', 'up'):
        return 'N'
    elif button in ('s', 'down'):
        return 'S'
    elif button in ('a', 'left'):
        return 'W'
    elif button in ('d', 'right'):
        return 'E'
    else:
        return None

class Controller(tk.Variable):
    def __init__(self, master, cli:UDPClient, speed_var:tk.IntVar, cmd_name:bytes, update_callback=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cli = cli
        self._cmd = cmd_name
        self._pressed = set()
        self.update_callback = update_callback
        self.speed_var = speed_var

    @property
    def pressed(self) -> list[str]:
        return list(self._pressed)

    @property
    def direction(self):
        if len(self.pressed) == 0:
            return 'XX'
        elif len(self.pressed) == 1:
            return self.pressed[0] * 2
        else:
            return ''.join(self.pressed)

    def add_pressed(self, button):
        button = parse_button(button)
        if button and not BUTTON_OPPOSITES[button] in self.pressed:
            print("Deteced Button", button)
            updated = button not in self._pressed
            self._pressed.add(button)
            if updated:
                self.send_command()
                if self.update_callback:
                    self.update_callback(self.pressed)

    def remove_pressed(self, button):
        button = parse_button(button)
        if button and button in self._pressed:
            updated = button in self._pressed
            self._pressed.discard(button)
            if updated:
                self.send_command()
                if self.update_callback:
                    self.update_callback(self.pressed)

    def send_command(self):
        self.cli.queue_command(self._cmd, struct.pack('2sB', self.direction.encode('ascii'), self.speed_var.get()))

class FootballWidget(tk.Frame):
    cmd_name = b'FBC'
    def __init__(self, master, cli, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cli = cli
        self.speed = tk.IntVar(self, 100, "SPEED")
        self.controller = Controller(self, self.cli, self.speed, cmd_name=self.cmd_name)
        self._active = False
        self.config(padx=10, pady=10)

        # ========== Buttons ==========
        self.btn_forward = ttk.Button(self, text='↑', width=4)
        self.btn_forward.grid(row=0, column=1)
        self.btn_backward = ttk.Button(self, text='↓', width=4)
        self.btn_backward.grid(row=1, column=1)
        self.btn_left = ttk.Button(self, text='←', width=4)
        self.btn_left.grid(row=1, column=0)
        self.btn_right = ttk.Button(self, text='→', width=4)
        self.btn_right.grid(row=1, column=2)
        self.btn_stop = ttk.Button(self, text='Stop', width=16)
        self.btn_stop.grid(row=2, column=0, columnspan=3)

        self._buttons = [self.btn_forward, self.btn_backward, self.btn_left, self.btn_right, self.btn_stop]
        # ========== Speed ==========
        self.speed_slider = ttk.Scale(self, from_=100, to=0, orient='vertical', variable=self.speed)
        self.speed_slider.grid(row=0, column=4, rowspan=3, padx=(10,0))
        self._bound_funcs = []

        self.deactivate()

    def set_active(self, state:bool):
        if state:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        if self._active:
            return
        self._active = True
        self._bound_funcs = [
            self.master.bind('<KeyPress>', self.key_press),
            self.master.bind('<KeyRelease>', self.on_release),
            self.master.bind('Shift', self.speed_up)
        ]
        for btn in self._buttons:
            btn['state'] = 'normal'
        self.speed_slider['state'] = 'normal'

    def deactivate(self):
        if not self._active:
            return
        self._active = False
        if self._bound_funcs:
            for funcid in self._bound_funcs:
                self.master.unbind(funcid)
        for btn in self._buttons:
            btn['state'] = 'disabled'
        self.speed_slider['state'] = 'disabled'

    def key_press(self, event):
        self.controller.add_pressed(event.char)

    def on_release(self, event):
        self.controller.remove_pressed(event.char)

    def speed_up(self, event):
        spd = self.speed.get()
        if spd < 255:
            self.speed.set(min(255, spd + 10))

    def slow_down(self, event):
        spd = self.speed.get()
        if spd > 0:
            self.speed.set(max(spd - 10, 0))

    def on_update(self, direction):
        if self.is_active():
            self.btn_forward.config(state='active' if 'N' in direction else 'normal')
            self.btn_backward.config(state='active' if 'S' in direction else 'normal')
            self.btn_right.config(state='active' if 'E' in direction else 'normal')
            self.btn_left.config(state='active' if 'W' in direction else 'normal')
            self.btn_stop.config(state='active' if direction == 'XX' else 'normal')

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Demo Football')
    active_var = tk.IntVar(root, 0)
    active = ttk.Checkbutton(root, text='Active', variable=active_var)
    active.pack()
    fw = FootballWidget(root, cli=UDPClient(), cmd_name='FBC')
    fw.pack()
    def act():
        if active_var.get() == 1:
            fw.activate()
        else:
            fw.deactivate()
    active['command'] = act
    root.mainloop()