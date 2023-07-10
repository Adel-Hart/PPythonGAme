import socket
import time


HOST = "192.168.1.43"
PORT = 7777

start = False
flagRoom = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ser:
    ser.connect((HOST, PORT))


    while True:
        if not start:
            data = ser.recv(1024).decode('utf-8')
            start = True
        if not flagRoom:
            msg = str(input())
            ser.sendall(msg.encode('utf-8'))
            print("전송완료, 이건 데이터")
            time.sleep(0.5)
            data = ser.recv(1024).decode('utf-8')
            print(data)

            if(msg == '1'):
                break
            if("joinRooms" in msg or "createRooms" in msg):
                flagRoom = True                 

        elif flagRoom:
            ser.sendall("im in Room".encode('utf-8'))
            print("방에 있음")
            data = ser.recv(1024).decode('utf-8')
            roomInfo = eval(data)           #!!보안 문제!! - data신뢰 확인 필요! (문자 검사등등)
            print("호스트는 이분 :{}, 맵코드는 이것 : {}".format(roomInfo[2]['Host'], roomInfo[1]['Map']))
            
    