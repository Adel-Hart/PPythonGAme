import socket
import time


HOST = "192.168.50.47"
PORT = 7777



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ser:
    ser.connect((HOST, PORT))


    while True:

        data = ser.recv(1024).decode('utf-8')
        print("이것이 내용 ")
        print(data)
        time.sleep(3)
        ser.sendall("quit".encode('utf-8'))
        print("테스트 끝")
        break