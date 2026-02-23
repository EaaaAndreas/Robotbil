# src/connectivity/porting.py
import socket
from machine import Pin
from connectivity.net_setup import wlan

indic = Pin(0, Pin.OUT, value=1)

led = Pin(2, Pin.OUT, value=0)

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

soc.bind(("0.0.0.0", 5001))

print(f'Listening for UDP on, {wlan.ipconfig('addr4')[0]}:5001')


try:
    while True:
        data, addr = soc.recvfrom(1024)
        print("Received from", addr, ":", data)

        led.toggle()
except Exception as e:
    indic.off()
    raise e