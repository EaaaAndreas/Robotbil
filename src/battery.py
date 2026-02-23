# src/battery.py
from machine import ADC

_bp = ADC(26)
_u16 = 2**16
_R1 = 9.9 # kOhm
_R2 = 4.7 # kOhm

battery_status = 0

def bat_update():
    global battery_status
    battery_status = _bp.read_u16() / _u16 * (_R1 + _R2) / _R2
    return 'B', battery_status