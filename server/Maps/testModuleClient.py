import socket
import time




HOST = "192.168.1.107"
PORT = 7777


socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.sendto("Connection Check", (HOST, PORT))
data = socket.recvfrom(1024)
print(f'Server : {data}')
while True:
    msg = str(input())
    socket.sendto(msg, (HOST, PORT))
    time.sleep(0.3)
    data = socket.recvfrom(1024)
    print('수신 완료 : {}'.format(data))



