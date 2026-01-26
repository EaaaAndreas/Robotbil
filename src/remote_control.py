# src/remote_control.py
import usocket as socket
from connectivity.network import wlan, init_wlan
from motor import motor1

if not wlan.isconnected():
    init_wlan()

with open("motor/control.html", "r") as f:
    HTML_TEXT = f.read()

def get_html(ip_addr:str) -> str:
    return HTML_TEXT.replace("{{ ipaddr }}", ip_addr)

def run_server():
    print("[SERVER] Setting up server")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen()

    while True:
        conn, addr = s.accept()
        print("[SERVER] connection from %s" % str(addr))
        request = conn.recv(1024)
        request = str(request)
        print("[SERVER] Content = %s" % request)
        idx = request.find('/cmd?c=')
        if idx > 0:
            cmd = request[idx+7]
            if cmd == "F":
                motor1.motorA_forward(2**15)
                motor1.motorB_forward(2**15)
            elif cmd == "B":
                motor1.motorA_backward(2**15)
                motor1.motorB_backward(2**15)
            elif cmd == "R":
                motor1.motorA_forward(2**15)
                motor1.motorB_backward(2**15)
            elif cmd == "L":
                motor1.motorA_backward(2**15)
                motor1.motorB_forward(2**15)
            elif cmd == "S":
                motor1.motorA_stop()
                motor1.motorB_stop()

        response = get_html(wlan.ipconfig('addr4')[0])
        conn.send('HTTP/.1. 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()


if __name__ == '__main__':
    run_server()