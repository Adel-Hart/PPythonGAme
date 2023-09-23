import socket
import time

host = '127.0.0.1'
port = 9999

con = (host, port)


# connection create
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while True:
    send_sock.sendto("test".encode(), con)
    data, addr = send_sock.recvfrom(1024)
    data = data.decode()
    print(f"Server:{data}")

send_sock.close()