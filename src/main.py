# /main.py
from sensor.multimeter import Voltmeter
from utime import sleep_ms

vm = Voltmeter()

while True:
    print(vm.voltage_calibrated())
    sleep_ms(500)
