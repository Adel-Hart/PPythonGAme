import socket
import time


HOST = "125.136.13.49"
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
            if "[" in data : roomInfo = eval(data)           #!!보안 문제!! - data신뢰 확인 필요! (문자 검사등등)
            print("호스트는 이분 :{}, 맵코드는 이것 : {}".format(roomInfo[2]['Host'], roomInfo[1]['Map']))
            data = ""

            msg = str(input())
            if("setMap" in msg):
                ser.sendall(("setMap-{}".format(msg.split('-')[1])).encode('utf-8'))
                time.sleep(0.1)
                data = ser.recv(1024).decode('utf-8')
                if(data == "Ok"):
                    data = ""
                    print("방 생성 완료")
                elif(data == "noRoom"):
                    data = ""
                    print("방 존재 x, 방을 업로드 하세요")

                else:
                    print(data)
                    data = ""

            

            
            
    