from connectivity.network import wlan, init_wlan
import network
import socket
from machine import Pin, PWM
import time

print('running wasd ')
# ==== MOTOR SETUP (same mapping as before) ====
ena = PWM(Pin(0))
in1 = Pin(1, Pin.OUT)
in2 = Pin(2, Pin.OUT)

enb = PWM(Pin(5))
in3 = Pin(3, Pin.OUT)
in4 = Pin(4, Pin.OUT)

ena.freq(1000)
enb.freq(1000)

def motorA_forward(speed=50000):
    in1.high()
    in2.low()
    ena.duty_u16(speed)

def motorA_backward(speed=50000):
    in1.low()
    in2.high()
    ena.duty_u16(speed)

def motorA_stop():
    in1.low()
    in2.low()
    ena.duty_u16(0)

def motorB_forward(speed=50000):
    in3.high()
    in4.low()
    enb.duty_u16(speed)

def motorB_backward(speed=50000):
    in3.low()
    in4.high()
    enb.duty_u16(speed)

def motorB_stop():
    in3.low()
    in4.low()
    enb.duty_u16(0)

def stop_all():
    motorA_stop()
    motorB_stop()

def forward():
    motorA_forward()
    motorB_forward()

def backward():
    motorA_backward()
    motorB_backward()

def left():
    motorA_backward()
    motorB_forward()

def right():
    motorA_forward()
    motorB_backward()


if not wlan.isconnected():
    init_wlan()

# ==== SIMPLE HTTP SERVER ====
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Listening on", addr)

def handle_command(cmd):
    if cmd == "F":
        forward()
    elif cmd == "B":
        backward()
    elif cmd == "L":
        left()
    elif cmd == "R":
        right()
    elif cmd == "S":
        stop_all()

while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()
    # Very simple parsing: look for /cmd?c=X
    first_line = request.split("\r\n")[0]
    # Example: GET /cmd?c=F HTTP/1.1
    path = first_line.split(" ")[1]

    if path.startswith("/cmd"):
        # extract c parameter
        # /cmd?c=F
        try:
            query = path.split("?", 1)[1]
            params = query.split("&")
            cmd = None
            for p in params:
                if p.startswith("c="):
                    cmd = p[2:]
                    break
            if cmd:
                handle_command(cmd)
            response = "OK"
        except:
            response = "ERR"
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n" + response)
    else:
        # basic root response
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nPico W motor server")
    cl.close()