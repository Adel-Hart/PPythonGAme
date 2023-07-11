import socket
import threading

Client = []

HOST = "192.168.1.41"
PORT = 7777

Clients = []

temp = ""

class Server(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self) #쓰레드를 클래스로 사용하는 경우는, 부모 클래스 생성자 호출 필요! >> 클래스 호출 시 run 함수 자동 실행
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024) #인자1 : 변경할 것, 인자2 : 데이터 크기지정 설정 (다음 인자에 크기가 나옴)
        self.sock.bind((HOST, PORT))


    def run(self):
        global Clients

        data, addr = self.receive() #통신 연결 테스트 및, ip얻기        
        Clients.append(addr)
        self.send(addr, context="ACK Ok")
        while True:
            data = self.receive()[0] #한무 대기
            if(data == "hi"):
                self.send(addr, "hi too")
                #for i in range(100):
                    #self.send(addr, str(i))
            

    def receive(self):
        global temp
        data, addr = self.sock.recvfrom(8388608) #데이터 받기, 인자는 데이터의 최대 크기        
        data = data.decode('utf-8')

        if(temp != data):
            temp = data 
            return data, addr
        elif(temp == data):
            return 0, 0 #전과 중복시 (같은 내용 수신시)


    def send(self, addr, context):
        self.sock.sendto(context.encode('utf-8'), addr)



ser = Server()
start = ser.start()