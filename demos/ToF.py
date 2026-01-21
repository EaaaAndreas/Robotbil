# /ToF.py
"""
Her kan man se, hvordan man får ToF sensoren til at fungere, med I2C
"""

# Imports
from umachine import Pin, I2C
from time import sleep_ms
from drivers.VL53L0X import VL53L0X as ToF # Jeg kalder driveren 'ToF' for nemhedens skyld

# Sleep for at være sikker på at Picoen er klar
sleep_ms(50)

print("ToF Test")

# Tænd sensoren (den har pin 19 -> vcc)
tof_vcc = Pin(19, Pin.OUT, value=1)

# Start Picoens I2C modul
i2c = I2C(scl=17, sda=16)

# Scan for at se, hvilke devices der er tilsluttet
devices = i2c.scan()
print("Scan result:", devices)
if not 0x29 in devices:
    raise Exception("ToF sensor not found")

# Start ToF driver
tof = ToF(i2c)

# Start målings loop
while True:
    # Start måling
    tof.start()

    # Aflæs måling
    print(tof.read())

    # Stop måling
    tof.stop()