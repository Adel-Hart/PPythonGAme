import threading
import socket
import re #정규식
import os
import zipfile

HOST = "192.168.50.47"
PORT = 8080


global roomList
roomList = []


class Room: #룸 채팅까지는 TCP 연결, 게임 시작 후는 TCP 연결 유지 한채로, UDP소켓 열기.
    def __init__(self, roomName): #Room(roomName)으로 객체 만들기
        self.whos = {} #식별자와 핸들러를 모아놓은 딕셔너리 > 주소(식별자) : 핸들러
        self.mapCode = 0
        self.inGame = False
        self.roomName = roomName
        self.startPos = []

    def joinRoom(self, client, addr, name):
        self.whos[addr] = client #목록에서 핸들러와 아이피 추가 
        print(addr)
        self.multiCastCmd(f"IN{name}, {addr}")

    def leaveRoom(self, client, addr, name):
        self.whos.pop(addr) #목록에서 핸들러와 아이피 지우기
        self.multiCastCmd(f"OUT{name}, {addr}")

    def setMap(self, mapCode):
        if(mapCode in os.listdir("./Maps")):
            self.mapCode = mapCode
            self.multiCastCmd(f"SETMAP{mapCode}")
            return "0080"
        else:
            return "0000"
        
    
    def startGame(self):
        




    def multiCastChat(self, msg): #방에 있는 모든 클라이언트에게 룸챗 메세지 전송
        for c in self.whos.values():
            c.sendMsg("roomChat" + msg)

    def multiCastCmd(self, msg): #방에 있는 모든 클라이언트에게 커맨드 메세지 전송
        for c in self.whos.values():
            c.sendMsg("CMD " + msg)



class Handler(): #각 클라이언트의 요청을 처리함 스레드로 분리!, TCP
    def __init__(self, soc, addr):
        self.soc = soc
        self.inRoom = False
        self.inGamePlayer = False
        print("실행 한다")
        self.run()
        print("실행 했다.")
        self.addr = addr[0]
        self.name = "" #플레이어 닉네임

    

    def makeRoom(self, roomName): #방 생성
        if not roomName in roomList:
            globals()["room" + roomName] = Room(roomName) #roomroomName의 변수 명으로 Room 클래스 선언(방을 팜)
            roomList.append(evaler(roomName)) #방 목록에 append, eval은 roomroomName을 호출하는 함수로, 클래스를 반환 함 즉, roomList엔 방이름의 인스턴스들이 있다.

            self.joinRoom(evaler(roomName))


            return True
        return False

    def joinRoom(self, roomName):
        if roomName in roomList:
            roomName.joinRoom(self, self.addr, self.name) #self는 클래스 자신을 의미, 즉 현재 핸들러를 보내려면 자기자신 self를 보낸다.
            #self.inRoom = True
            return True
        return False
    

    


    def checkRoom(self):
        print("checkroom")
        result = '!'.join(x.roomName for x in roomList)#roomList를 문자열로 '!'를 사용하여 구분하여 문자열로 만듬 , + 메모리 절약으로 실행속도 개선
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



    def sendMsg(self, msg: str):
        self.soc.send(msg.encode())
        return True


    def run(self):
        msg = threading.Thread(target = self.recvMsg, args = ())
        msg.start()



    
def checkMapList():
    result = '!'.join(os.listdir("./Maps")) #Maps 디렉토리의 맵 파일 이름들을 가져와 문자열로 만들기
    return result

def evaler(self, cmd: str): #eval 함수 실행기, 그 자체로 취약점이기 때문에 함수로 만듬, 주로 room+방이름으로 된 방 객체를 호출하기 위함.
    try:
        if(cmd != ""): #인젝션을 통한 해킹 방지를 위해, 정규식으로 해결!
            result = re.sub(r"[^a-zA-Z0-9_]", "", cmd) #문자 숫자 빼고 전부 삭제 
            return eval("room"+cmd)
        else:
            return False
    except:
        return False


class udpGame(): #인 게임에서 정보를 주고 받을 udp소켓


    def __init__(self, clients: list, room: Room): #clients : 참여자들 ip '리스트', room : 방 핸들러

        self.room = room #udp가 실행된 room 방 객체를 가져온다.
        self.clientPos = {}
        self.rgb = [0, 0, 0] #rgb 값 저장할 리스트
        self.change = self.rgb #rgb의 변화량 감지 리스트

        for c in clients:
            self.clientPos[c] = "0, 0" #클라이언트 ip : "x, y" 위치정보를 저장
            

        
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.bind((HOST, PORT)) #클래스 인스턴트를 만들면 udp소켓 열기
        print("udp game server listening")

        recv = threading.Thread(target= self.recvMsg)
        recv.start()
    
    def recvMsg(self): #클라이언트로의 메세지를 분별 및 확인하여 전송
        while(True):
            msg, fromAddr = self.udpSock.recvfrom(1024)
            msg = msg.encode()
            fixAddr = fromAddr[0] #fromAddr 리턴이 (아이피, 소켓주소)라서
            msg = msg.split('!') #!로 구분함  >  형식 : !방이름!위치정보
                                # RGB변경시 메세지 > 형식 : _!방이름!R,G,B
            #방 이름이 없는데 요청한경우 오류가 나기 때문에.
            if(msg[1] == self.room.roomName): #해당 방이름의 요청에만 응답!
                if(msg[0] == "_"): #RGB변경 메세지 일때
                    self.rgb[0] = msg[2].spilt(',')[0]
                    self.rgb[1] = msg[2].spilt(',')[1]
                    self.rgb[2] = msg[2].spilt(',')[2] #Rgb정보 저장

                else: #위치정보 저장 (거의 대부분 이게 요청 됨.)
                    self.clientPos[fixAddr] = msg[2]
            self.sendMsg(fromAddr) #리턴



    def sendMsg(self, sendAddr):
        if(self.change == self.rgb): #rgb값이 변하지 않았을 때는, 위치정보만 전달.
            for c in self.clientPos.keys():
                self.udpSock.sendto("{}", sendAddr)  # 문자열 형태로 위치정보 전달(구분문자 ?) !          

        else:
            #rgb의 값을 클라이언트에게 전송 + 그 후 위치정보도 같이 전달
            self.change = self.rgb
        change = self.rgb
        




'''
루트 1: 위치가 바뀔때 마다 클라이언트가 위치 정보 전송

루트 2: 계속 while문으로 바뀐 위치정보를 계속 전달한다. 
    이때 서버가 다루는건 오직RGB와 위치 만이다.
    다른 플레이어가 도착지점에 도착하여 모습이 보이지 않는건 클라이언트에서 연산.

    >>서버에선 스레드로 위치정보를 받아, 해당 룸에서 실행된 UDP객체의 지역변수에 저장하고
        동시에 스레드로 그 위치정보를 읽어, 방 목록에 있는 아이피들에게 전송한다.

        주의 할 점, 플레이어 여러명이 데이터를 거의 동시에 보내니, UDP리시버와 센더를 스레드 하나씩 쓰면, 버퍼가 쌓임
        > 그래도 스레드를 늘리면, 서버가 과부화 및 오히려 속도 저하될 수도 있으니, 일단은 단일 스레드로 써보자 (리시버 함수의 데이터 저장하는 속도를 믿어보자!)

        <루트2 이게 더 좋을 듯?>



'''
                





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