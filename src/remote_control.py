# src/remote_control.py
import usocket as socket
from connectivity.network import wlan, init_wlan
from motor import motor1

# Check om der er internet
if not wlan.isconnected():
    init_wlan()

# Indlæs HTML-filen (som global værdi)
with open("motor/control.html", "r") as f:
    HTML_TEXT = f.read()


def get_html(ip_addr:str) -> str:
    """
    Returner HTML-filen som str, med de variable der skal erstattes
    :param ip_addr: Picoens IP adresse fx. '10.110.0.51'
    :type ip_addr: str
    :return: Den formatterede HTML-kode
    :rtype: str
    """
    # Lav HTML-koden som en variabel
    out = HTML_TEXT
    # Erstat '{{ variabel }}' med variablen
    out.replace("{{ ipaddr }}", ip_addr)
    return out

def run_server() -> None:
    """
    Kør en server, der tager input fra tastaturet, og får bilen til at køre
    :return: None
    """
    print("[SERVER] Setting up server") # Debug

    # Start socket og sæt det op på picoens IP - port 80 (HTTP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # FIX ME: `SOCK_STREAM` er TCP protokol. Den kan ændres til `socket.SOCK_DGRAM` for at bruge UDP (user DataGRAM protocol). Men så skal der nok også rettes til, andre steder i koden.
    s.bind(('', 80))
    s.listen()

    while True:
        # Opret forbindelse til porten
        conn, addr = s.accept()
        print("[SERVER] connection from %s" % str(addr)) # Debug

        # Hent forspørgslen og lav den om til tekst
        request = conn.recv(1024)
        request = str(request)

        print("[SERVER] Content = %s" % request) # Debug

        # Find ud af, hvor der står '/cmd?c=' - det er begyndelsen af vores input-kommando
        idx = request.find('/cmd?c=')
        if idx > 0: # Hvis idx > 0 så er kommandoen fundet. Hvis den ikke findes, er idx = -1
            # Kommandoen er det første bogstav efter '/cmd?c='
            cmd = request[idx+7]
            if cmd == "F":
                # Kør frem
                motor1.motorA_forward(2**16)
                motor1.motorB_forward(2**16)
            elif cmd == "B":
                # Kør baglens
                motor1.motorA_backward(2**16)
                motor1.motorB_backward(2**16)
            elif cmd == "R":
                # Drej til højre
                motor1.motorB_forward(2**16)
                motor1.motorA_backward(2**16)
            elif cmd == "L":
                # Drej til venstre
                motor1.motorB_backward(2**16)
                motor1.motorA_forward(2**16)
            elif cmd == "S":
                # Stop
                motor1.motorA_stop()
                motor1.motorB_stop()

        # Hent html som str
        response = get_html(wlan.ipconfig('addr4')[0])
        # Send HTTP-headers
        conn.send('HTTP/.1. 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        # Send sidens indhold
        conn.sendall(response)
        # Stop med at sende
        conn.close()


if __name__ == '__main__':
    run_server()