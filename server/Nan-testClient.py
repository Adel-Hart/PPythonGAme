import socket
import time


# connection create
send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send_sock.connect(('127.0.0.1', 9999))

while True:
    send_sock.send("adfaf".encode())
    time.sleep(10)

send_sock.close()