import socket
import time


# connection create
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_sock.bind(('127.0.0.1', 9999))


while True:
    data, addr = send_sock.recvfrom(1024)
    data = data.decode()
    print(f"Client:{addr}")
    send_sock.sendto("hi".encode(), addr)

send_sock.close()