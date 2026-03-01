# demos/ir.py

# Importer
from umachine import Pin, ADC
from utime import sleep_ms

# Tænd sensoren
power = Pin(20, Pin.OUT, value=1)

# Start picoens ADC (Analog-Digital-Converter) modul
adc = ADC(Pin(27))

# Aflæs
while True:
    # Aflæs
    print(adc.read_u16())
    # Vent (så lortet ikke crasher)
    sleep_ms(100)