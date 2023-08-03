import socket
import threading


HOST = "192.168.50.47"
PORT = 8080

#https://gogetem.tistory.com/entry/Python%EC%9D%98-%EA%B0%84%EB%8B%A8%ED%95%9C-UDP-%EC%B1%84%ED%8C%85%EB%B0%A9-%EB%A7%8C%EB%93%A4%EA%B8%B0

Clients = []

temp = ""

class Server(threading.Thread):

    def __init__(self, socket):
        #threading.Thread.__init__(self) #쓰레드를 클래스로 사용하는 경우는, 부모 클래스 생성자 호출 필요! >> 클래스 호출 시 run 함수 자동 실행
        super().__init__()
        self.sock = socket
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024) #인자1 : 변경할 것, 인자2 : 데이터 크기지정 설정 (다음 인자에 크기가 나옴)
        self.sock.bind((HOST, PORT))

#https://hyeonukdev.tistory.com/117


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