import socket

# connection create
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = ("127.0.0.1", 9999)

# send to dest
send_sock.sendto("1".encode(), dest)

data, con = send_sock.recvfrom(1024)
print(data)
send_sock.close()