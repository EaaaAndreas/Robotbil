# src/battery.py
from machine import ADC

_bp = ADC(26)
BATTMAX = 8.4
_u16 = 2**16
_R1 = 10 # kOhm
_R2 = 4.7 # kOhm

battery_status = 0

def bat_update(*_):
    global battery_status
    battery_status = _bp.read_u16() * 3.3 / _u16 * (_R1 + _R2) / _R2
    print("Battery", battery_status)
    return min(255, int(battery_status / BATTMAX * 255)),