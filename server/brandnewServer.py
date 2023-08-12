import threading
import socket
import random


HOST = ""
PORT = 8080


global rooms
rooms = []

class Room: #룸 채팅까지는 TCP 연결, 게임 시작 후는 TCP 연결 유지 한채로, UDP소켓 열기.
    def __init__(self):
        self.clients = [] #방에 있는 클라이언트 핸들러 목록
        self.clients_name = [] #방에 있는 클라이언트 식별자 목록 (아이피)
        self.mapCode = 0
        self.inGame = False

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
        self.addr = addr
        self.inRoom = False
        self.inGamePlayer = False
        self.run()

    def makeRoom(self, roomCode): #방 생성
        if not roomCode in rooms:
            globals()[roomCode] = Room() #roomCode의 변수 명으로 Room 클래스 선언(방을 팜)
            rooms.append(roomCode) #방 목록에 append
            return True
        return False

    def joinRoom(self, roomCode, addr):
        if roomCode in rooms:
            roomCode.join(addr)
            self.inRoom = True
            return True
        return False
    

    def recvMsg(self):
        while True:
            data = self.soc.recv(1024)
            msg = data.decode()



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
    t = threading.Thread(target = Handler, args= (conn, addr))