import socket

# socket create
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
recv_address = ('127.0.0.1', 9999)
sock.bind(recv_address)

data_size = 1024
while True:
    data, sender = sock.recvfrom(data_size)
    print(sender)
    print(data.decode())
    sock.sendto("dafag".encode(), ('127.0.0.1', 9999))
sock.close()