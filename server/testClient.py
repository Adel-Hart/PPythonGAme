import socket
import time


HOST = "192.168.1.17"
PORT = 7777

start = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ser:
    ser.connect((HOST, PORT))


    while True:
        if not start:
            data = ser.recv(1024).decode('utf-8')
            start = True
        msg = str(input())
        ser.sendall(msg.encode('utf-8'))
        print("전송완료, 이건 데이터")
        time.sleep(0.5)
        data = ser.recv(1024).decode('utf-8')
        print(data)

        if(msg == '1'):
            break

    