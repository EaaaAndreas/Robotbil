# /main.py
import socket
import machine
import ustruct



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.bind(('0.0.0.0', 50001))

    while True:
        data, addr = sock.recvfrom(1024)
        print(data[0], data[1:], addr)
        if data[1:] == b'DISCOVER':
            sock.sendto(bytes([data[0]]) + b'OFFER', addr)
        elif data[1:] == b'REQUEST':
            sock.sendto(bytes([data[0]]) + b'ACCEPT', addr)

finally:
    sock.close()