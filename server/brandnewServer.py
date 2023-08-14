import threading
import socket
import random


HOST = "192.168.50.47"
PORT = 8080


global roomList
roomList = []

class Room: #룸 채팅까지는 TCP 연결, 게임 시작 후는 TCP 연결 유지 한채로, UDP소켓 열기.
    def __init__(self, roomName):
        self.clients = [] #방에 있는 클라이언트 핸들러 목록
        self.clients_name = [] #방에 있는 클라이언트 식별자 목록 (아이피)
        self.mapCode = 0
        self.inGame = False
        self.roomName = roomName

    def join(self, client, addr):
        self.clients.append(client) #클라이언트를 받고, 목록에 추가
        self.clients_name.append(addr) #아이피 목록에 추가
        self.multiCast(addr + " 접속")

    def leave(self, client, addr):
        self.clients.remove(client) #클라이언트를 받고, 목록에서 지우기
        self.clients_name.remove(addr) #아이피 목록에서 지우기
        self.multiCast(addr + " 나감")


    def multiCastChat(self, msg): #방에 있는 모든 클라이언트에게 룸챗 메세지 전송
        for c in self.clients:
            c.sendMsg("roomChat" + msg)

    def multiCastCmd(self, msg): #방에 있는 모든 클라이언트에게 커맨드 메세지 전송
        for c in self.clients:
            c.sendMsg("CMD " + msg)
    

    



class Handler(): #각 클라이언트의 요청을 처리함 스레드로 분리!, TCP
    def __init__(self, soc, addr):
        self.soc = soc
        self.inRoom = False
        self.inGamePlayer = False
        print("실행 한다")
        self.run()
        print("실행 했다.")
        self.addr = addr
        self.name = "" #플레이어 닉네임


    def makeRoom(self, roomName): #방 생성
        if not roomName in roomList:
            globals()[roomName] = Room() #roomName의 변수 명으로 Room 클래스 선언(방을 팜)
            roomList.append(roomName) #방 목록에 append

            self.joinRoom(roomName)
            return True
        return False

    def joinRoom(self, roomName):
        if roomName in roomList:
            roomName.join(self.addr)
            self.inRoom = True
            return True
        return False
    

    


    def checkRoom(self):
        print("checkroom")
        result = '!'.join(str(x) for x in roomList)#roomList를 문자열로 '!'를 사용하여 구분하여 문자열로 만듬 , + 메모리 절약으로 실행속도 개선
        return result #결과 값 반환.


    def recvMsg(self): #클라이언트로 부터의 메세지 수신 핸들러
            while True:
                
                print("data listening..")
                data = self.soc.recv(1024)
                print("get data")
                msg = data.decode()


                if not self.inRoom: #방 목록 탐색기에 있을때.
                    if msg == "0000":
                        print("ok")
                        self.soc.send("0080".encode()) #OK sign
                    if "0001" in msg: #이름 설정, 수신 형식 0001이름    ex) 0001ADEL
                        self.name = msg.replace("0001", "") #잘라내기 이름 설정
                        self.soc.send("0080".encode()) #OK sign
                    if msg == "0002": #방 목록 수신
                        result = self.checkRoom() #함수값이 룸 리스트, 형식은 !로 구분함  ex)roomna!jai123!kurukuru!bang
                        self.soc.send(result.encode())

                    if "0003" in msg: #방 만들기 수신 형식은 0003방이름
                        self.makeRoom(msg.split('3')[1])
                        self.soc.send("0080".encode())


    def run(self):
        msg = threading.Thread(target = self.recvMsg, args = ())
        msg.start()





sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen()
print("서버 시작")



while True:
    conn, addr = sock.accept()
    print("연결됨")
    t = threading.Thread(target = Handler, args= (conn, addr)) #(conn, addr) 형식이 아니면 오류, 스트링으로 읽어서 그런듯? (conn, )으로 써도 가능
    t.start()

socket.close()