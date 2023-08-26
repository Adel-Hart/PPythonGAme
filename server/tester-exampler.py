import socket
import threading

# socket create
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
recv_address = ('127.0.0.1', 9999)
sock.bind(recv_address)
sock.listen()

data_size = 1024

def recv1(sock):
    while True:
        print(f"1 : {sock.recv(1024).decode()}")

def recv2(sock):
    while True:
        print(f"2 : {sock.recv(1024).decode()}")


while True:
    conn, addr = sock.accept()

    t1 = threading.Thread(target=recv1, args=(conn, ))
    t2 = threading.Thread(target=recv1, args=(conn, ))
    t1.start()
    t2.start()


