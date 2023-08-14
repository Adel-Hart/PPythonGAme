import socket
import threading


HOST = ""
PORT = 8080



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recv_address = (HOST, PORT)
sock.connect(recv_address)

print("연결 성공")
while True:
    s = str(input())

    sock.send(s)

    data = sock.recv(1024)

    print(data)

sock.clos()
