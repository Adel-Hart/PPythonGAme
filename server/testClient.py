import socket

# connection create
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = ("127.0.0.1", 9999)

while True:
    print("반복 시작")

    a = str(input())

    send_sock.sendto(a.encode(), dest)
    print("전송완료 rmflrh")

    data, con = send_sock.recvfrom(1024)
    print(data.decode() + " 이건 주소 --> ", con)
    


send_sock.close()