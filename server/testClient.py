import socket
import threading
import select

HOST = "118.40.40.181"
PORT = 8080



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recv_address = (HOST, PORT)
sock.connect(recv_address)

print("연결 성공")




def recv(sock):
    sock.settimeout(300000)
    
    while True:
        
        data = sock.recv(1024)
        print(data.decode())


def send(sock):
    while True:
        data = str(input())
        sock.send(data.encode())
        print("me :{}".format(data))
        if(data == "q"):
            socket.close()

t1 = threading.Thread(target=recv, args=(sock, ))
t1.start()

t2 = threading.Thread(target=send, args=(sock, ))
t2.start()

        

