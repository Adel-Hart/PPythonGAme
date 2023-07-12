import socket
import time
import threading




HOST = "192.168.1.26"
PORT = 7777


socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.sendto("Connection Check".encode('utf-8'), (HOST, PORT))


data = socket.recvfrom(1024)[0].decode('utf-8')
print(f'Server : {data}')
while True:
    msg = str(input())
    socket.sendto(msg.encode('utf-8'), (HOST, PORT))
    time.sleep(0.3)

    data = socket.recvfrom(1024)[0].decode('utf-8')

    print('수신 완료 : {}'.format(data))


