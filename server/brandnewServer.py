import threading
import socket
import re #정규식
import os
import sys
import selectors
from datetime import datetime
import time

with open("./serverip.txt","r") as f:
    HOST = f.readline()

PORT = 8080

sele = selectors.DefaultSelector() #셀렉터 생성



global roomList
roomList = []

players = []


class Room: #룸 채팅까지는 TCP 연결, 게임 시작 후는 TCP 연결 유지 한채로, UDP소켓 열기.
    def __init__(self, roomName): #Room(roomName)으로 객체 만들기
        self.whos = {} #ip와 핸들러를 모아놓은 딕셔너리 > ip(식별자) : 핸들러
        self.mapCode = ""
        self.inGame = False
        self.roomName = roomName
        self.startPos = []

        self.whosReady = {} #닉네임 : 준비 여부


    

    def joinRoom(self, client, addr, name):
        self.whos[addr] = client #목록에서 핸들러와 아이피 추가 
        self.whosReady[name] = False #준비 목록에 추가 + 플레이어 ip가 아닌 이름을 사용하는 리스트로도 겸용한다.
        print(addr)
        #self.castCmd("INFO"+"!".join(self.whos.keys()), client) #접속한 플레이어 에게만, 방 인원 정보
        #self.multiCastCmd(f"IN{name}, {addr}") #플레이어들에게, 플레이어 추가 로그

    def leaveRoom(self, addr, name):
        self.whos.pop(addr) #목록에서 핸들러와 아이피 지우기
        self.whosReady.pop(name, None) #준비 목록에서 이름 빼고, 오류 날시 오류대신 None반환
        self.multiCastCmd(f"OUT{name}, {addr}")

    def setMap(self, mapCode):
        if mapCode in os.listdir("./Maps"):
            self.mapCode = mapCode
            #self.multiCastCmd(f"SETMAP{mapCode}")
            return "0080"
        else:
            return "0000"


    
    def startGame(self):
        self.inGame = True
        self.gameHandler = udpGame(self.whos.keys(), self) #참여자 ip리스트와 방 핸들러를 넣어준다.
        self.gameHandler.run()

    def endGame(self):
        self.inGame = False
        for c in self.whos.values():
            c.inGamePlayer = False #각 핸들러의 inGamePlayer신호 끄기
            
        del self.gameHandler #gameHandler 인스턴스 삭제
        


    def multiCastChat(self, msg, name): #방에 있는 모든 클라이언트에게 룸챗 메세지 전송
        for c in self.whos.values():
            c.sendMsg(f"roomChat!{name}:{msg}") #!로 구분, 닉네임 : 내용

    def multiCastCmd(self, msg): #방에 있는 모든 클라이언트에게 커맨드 메세지 전송
        for c in self.whos.values():
            c.sendMsg("CMD " + msg)

    def castCmd(self, msg: str, target: classmethod): #접속한 특정 ip에게 메세지 반환 target:핸들러자체
        target.sendMsg("CMD " + msg) 

    def deleteRoom(self):
        roomList.remove(self) #방목록에서 삭제
        del self #자신의 참조 삭제

class Handler(): #각 클라이언트의 요청을 처리함 스레드로 분리!, TCP
    def __init__(self, soc, addr):
        self.soc = soc
        self.inRoom = False
        self.inGamePlayer = False
        self.addr = addr[0]
        self.name = "" #플레이어 닉네임
        self.inEditor = False #에디터화면 일때
        self.alive = True
        self.aliveStack = 0 #최대 몇번까지 봐줄건가

        self.run() #시작 함수는 모든 변수 설정 후 마지막에 호출!!
        
        

    def run(self): #시작
        
        #heatBeatThread = threading.Thread(target = self.heartBeat) #하트비트 시작
        #heatBeatThread.start()
        recvThread = threading.Thread(target=self.recvMsg) #받기 시작
        recvThread.start()


    def shutDown(self): #종료
        
        self.soc.close()
        players.remove(self.name)
        print("shutdown the thread")
        del self

    
    def heartBeat(self): #클라이언트의 접속 끊어짐을 확인하면, 데이터를 지우고 소켓을 닫는다
        while True:
            self.alive = False
            time.sleep(10) #30초에 한번씩
            if self.alive:
                self.alive = False #문제 없음
                self.aliveStack = 0
                print(f"{self.addr} 잘 살아잇다!")
            else:
                self.alive = False
                self.aliveStack += 1 #스택 +1
                print(f"{self.addr} 어른이 말하면 들어야지!")
            
            
            
            
            if self.aliveStack > 3: #4번 이상 무시하면
                print(f"{self.addr} no heart") 
                self.aliveStack = 0
                self.shutDown()
                break
            else:
                pass
            
        sys.exit() #현재 스레드 종료     

            


    def makeRoom(self, roomName): #방 생성
        if roomName not in roomList:
            globals()["room" + roomName] = Room(roomName) #roomroomName의 변수 명으로 Room 클래스 선언(방을 팜)
            roomList.append(evaler(roomName)) #방 목록에 append, eval은 roomroomName을 호출하는 함수로, 클래스를 반환 함 즉, roomList엔 방이름의 인스턴스들이 있다.
            self.soc.send("0080".encode()) #방 만들기 성공
            print("방 만들기 성공")
        
            return self.joinRoom(evaler(roomName))

        print("방 제작 실패")
        return False

    def joinRoom(self, roomName):
        if roomName in roomList:
            roomName.joinRoom(self, self.addr, self.name) #self는 클래스 자신을 의미, 즉 현재 핸들러를 보내려면 자기자신 self를 보낸다.
            self.inRoom = True
            self.roomHandler = roomName #클래스에 핸들러 설정
            return True
        return False
    

    def leaveRoom(self):
        print("leaving room..")
        self.inRoom = False
        self.roomHandler.leaveRoom(self.addr, self.name) #방 핸들러에서 자신의 정보 제거
        del self.roomHandler #조심 del 함수는 참조를 없애는거기 때문에, 룸 핸들러가 없어지는게 아님
            #룸 핸들러의 참조가 모두 사라지면, 파이썬의 garbage collector가 자동으로 룸 핸들러를 삭제시킴
        
        return True


    def checkRoom(self):
        print("checkroom")
        result = '!'.join(x.roomName for x in roomList)#roomList를 문자열로 '!'를 사용하여 구분하여 문자열로 만듬 , + 메모리 절약으로 실행속도 개선
        if result:
            return result #결과 값 반환.
        else:
            return "NULL"

    def recvMsg(self: classmethod): #클라이언트로 부터의 메세지 수신 핸들러
            while True:

                data = self.soc.recv(1024)


                print(f"{datetime.now()} :  {self.addr}")
                msg = data.decode()

                print(msg)

                if msg == "7777": #heartBeat 신호
                    self.alive = True #요청보내면 살아있다 표시
                    self.soc.send("0080".encode())
                    

                
                elif msg == "9999": #연결 종료 사안
                    self.shutDown()
                    sys.exit() #현재 스레드 종료
                    
                elif "2000" in msg:

                        reqMap = msg.replace("2000CODE", "") #2000을 보냈으면, 맵 코드를 보낸다.
                        print("이게 맵 " + reqMap)
                        
                        if reqMap in os.listdir("./Maps"): #!로 구분된 문자열이 출력이라, 변환해야 함
                                print("0000 전송")
                                self.soc.send("0000".encode()) #이미 존재

                        else:
                            print("0080전송")
                            self.soc.send("0080".encode()) #전송시작.
                            
                            with open(f"./Maps/{reqMap}.dat", "w") as f: #파일 읽어서 저장 시작
                                print("파일 읽기")
                                try:
                                    print("2")
                                    stream = self.soc.recv(1024).decode() #먼저 1024를 읽는다.
                                    print(bool(stream))
                                    end = True
                                    while end: #EOF명령을 받으면, 쓰기 종료
                                        f.write(stream) #stream 쓰기
                                        print("받아오는중,,,")
                                        if stream.strip()[-1] == "*": #마지막 문자가 *이면 (종료면)
                                            end = False #종료
                                            stream = 0
                                        else:
                                            stream = self.soc.recv(1024) #다시 1024만큼 읽는다. 이런 순서로 하면, 코드가 단축화 된다.

                                    print("완료")
                                    f.close() #파일 저장
                                    self.soc.send("0080".encode()) #성공 메세지 전송
                                    print("완료 전송")
                                    self.inEditor = False
                                    print("소켓 닫기")
                                    self.soc.close() #소켓 닫기
                                    break

                                except Exception:
                                    self.soc.send("0000".encode()) #오류 메세지 전송
                                    print("오류 전송") 
                                    self.inEditor = False
                                    self.soc.close() #소켓 닫기
                                    break

                if not self.inRoom: #방 목록 탐색기에 있을때.
                    if msg == "0000":
                        print("ok")
                        self.soc.send("0080".encode()) #OK sign
                    elif "0001" in msg: #이름 설정, 수신 형식 0001이름    ex) 0001ADEL
                        if not msg in players:
                            self.name = msg.replace("0001", "") #잘라내기 이름 설정
                            players.append(self.name) #플레이어 목록에 이름추가
                            self.soc.send("0080".encode()) #OK sign

                        else:
                            self.soc.send("0000")
                    elif msg == "0002": #방 목록 수신
                        result = self.checkRoom() #함수값이 룸 리스트, 형식은 !로 구분함  ex)roomna!jai123!kurukuru!bang
                        self.soc.send(result.encode())

                    elif "0003" in msg: #방 만들기 수신 형식은 0003방이름
                        self.makeRoom(msg.split('3')[1])
                        #0080 수신은, 방 join하면 방목록을 보내버려서, 그 전에 보내긱 위해, makeRoom 안에존재.


                    






                else: #방 목록 탐색기가 아닐 때 (방 안 or 게임 중)
                    if msg == "0002": #방 목록 수신
                        result = self.checkRoom() #함수값이 룸 리스트, 형식은 !로 구분함  ex)roomna!jai123!kurukuru!bang
                        self.soc.send(result.encode())
                    
                    # 디버그






                    elif msg == "1000": #맵 목록 조회
                        print("맵 view")
                        self.soc.send(checkMapList().encode())
                    elif "1001" in msg: #맵 설정 형식 >> 1001!MapCode >>0080 송신
                        mapCode = msg.split("!")[1]
                        self.roomHandler.setMap(mapCode)
                        self.soc.send("0080".encode())

                    elif msg == "1002": #게임 시작
                        self.roomHandler.startGame()
                        self.inGamePlayer = True
                    elif msg == "1003": #방 나가기

                        if len(self.roomHandler.whos.keys()) == 1: #1명일때
                            self.roomHandler.deleteRoom() #삭제 요청
                            del self.roomHandler #핸들러 참조 삭제
                            self.inRoom = False
                            self.soc.send("0080".encode())

                        else:
                            if self.leaveRoom():
                                self.inRoom = False
                                self.soc.send("0080".encode())
                            else:
                                self.soc.send("0000".encode())

        

                    elif msg == "1004": #방 파쇄 (플레이어가 1명 밖에 없을때만 가능)
                        if len(self.roomHandler.whos.keys) == 1:
                            self.roomHandler.deleteRoom() #삭제 요청
                            del self.roomHandler #핸들러 참조 삭제
                            
                            self.inRoom = False
                            self.soc.send("0080".encode()) #완료메세지
                        else:
                            self.soc.send("0000".encode())


                    elif msg == "1005": #방 정보 요청
                        self.soc.send(self.sendRoomInfo().encode())



                    
                                





    def sendMsg(self, msg: str):
        self.soc.send(msg.encode())
        return True


    def sendRoomInfo(self):
        #방이름, 방 플레이목록, 맵 코드, 플레이어 준비현황(맵 다운됐을 때 준비가능), 게임시작여부
        
        '''
        클라이언트 측에서, 1초 간격으로 방 정보를 요청함
        
        형식 : 방이름!플레이어목록(@로 구분)!맵 코드(없으면 None)!플레이어 준비 현황({플레이어 : True or False}을 문자열로 )!True or False
        '''


        infoData = f"{self.roomHandler.roomName}!{str(list(self.roomHandler.whosReady.keys()))}!{self.roomHandler.mapCode}!{str(self.roomHandler.whosReady)}!{self.roomHandler.inGame}"
        return infoData
        #.keys()는 dic_list객체라, list로 만들고 다시 문자열 str로 감싸야 함




   # def run(self):
        #msgRecv = threading.Thread(target = self.recvMsg, args = (self,)) #메세지 받는 스레드 시작 (스레드는 개별 객체라 self를 보내줘야 함)
        #msgRecv.start()
    #    self.recvMsg()


    
def checkMapList():
    result = '!'.join(os.listdir("./Maps")) #Maps 디렉토리의 맵 파일 이름들을 가져와 문자열로 만들기
    return result

def evaler(cmd: str): #eval 함수 실행기, 그 자체로 취약점이기 때문에 함수로 만듬, 주로 room+방이름으로 된 방 객체를 호출하기 위함.
    try:
        if cmd != "": #인젝션을 통한 해킹 방지를 위해, 정규식으로 해결!
            result = re.sub(r"[^a-zA-Z0-9]", "", cmd) #문자 숫자 빼고 전부 삭제 
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
            

        
        

    def run(self):

        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.bind((HOST, PORT)) #클래스 인스턴트를 만들면 udp소켓 열기
        print("udp game server listening")

        sele.register(self.udpSock, selectors.EVENT_READ, self.recvMsg)
        #사용자가 연결시 recvMsg를 통해 메세지를 받고, 데이터를 리턴해 전송

        while True: #셀렉터를 통해, 데이터 수신시 스레드(비스무리) 생성
            events = sele.select() #이벤트 감지
            for key, mask in events:
                callback = key.data #콜백함수 적용 key.data = 실행되는 함수(괄호 안에 쓴것)
                callback(key.fileobj) #함수 실행 인자는 key.fileobj >  register(fileobj, events, data=None)¶

    
    def recvMsg(self): #클라이언트로의 메세지를 분별 및 확인하여 전송
        while(True):
            msg, fromAddr = self.udpSock.recvfrom(1024)
            msg = msg.encode()
            fixAddr = fromAddr[0] #fromAddr 리턴이 (아이피, 소켓주소)라서
            msg = msg.split('!') #!로 구분함  >  형식 : !방이름!위치정보
                                # RGB변경시 메세지 > 형식 : _!방이름!R,G,B
                                #게임 종료 메세지 > @!
            #방 이름이 없는데 요청한경우 오류가 나기 때문에.
            if msg[1] == self.room.roomName: #해당 방이름의 요청에만 응답!
                if msg[0] == "_": #RGB변경 메세지 일때
                    self.rgb[0] = msg[2].spilt(',')[0]
                    self.rgb[1] = msg[2].spilt(',')[1]
                    self.rgb[2] = msg[2].spilt(',')[2] #Rgb정보 저장

                elif msg[0] == "": #위치정보 저장 (거의 대부분 이게 요청 됨.)
                    self.clientPos[fixAddr] = msg[2]
                elif msg[0] == "@":
                    self.room.multiCastCmd("GAMEOUT") #TCP모듈에 게임 끝 선언
                    self.udpSock.close() #udp소켓 닫기
                    self.room.endGame() #방에 게임 끝 신호 보내기 (GameHandler 인스턴스 삭제)

            self.sendMsg(fromAddr) #리턴



    def sendMsg(self, sendAddr):
        if self.change == self.rgb: #rgb값이 변하지 않았을 때는, 위치정보만 전달.  >>위치정보는 P로 시작, RGB는 R로 시작
            res = "P"
            for c in self.clientPos.keys():
                res += f"{c}:{self.clientPos[c]}!"   #"P192.168.0.1:20,1!981.352.21.62:20,6!.."   
            self.udpSock.sendto(res.encode(), sendAddr) #전송
        else:
            #rgb의 값을 클라이언트에게 전송 + 그 후 위치정보도 같이 전달
            self.change = self.rgb
            res = ",".join(self.rgb)
            self.udpSock.sendto(f"R{res}".encode(), sendAddr)
        




'''
루트 1: 위치가 바뀔때 마다 클라이언트가 위치 정보 전송

루트 2: 계속 while문으로 바뀐 위치정보를 계속 전달한다. 
    이때 서버가 다루는건 오직RGB와 위치 만이다.
    다른 플레이어가 도착지점에 도착하여 모습이 보이지 않는건 클라이언트에서 연산.

    >>서버에선 스레드로 위치정보를 받아, 해당 룸에서 실행된 UDP객체의 지역변수에 저장하고
        동시에 스레드로 그 위치정보를 읽어, 방 목록에 있는 아이피들에게 전송한다.

        주의 할 점, 플레이어 여러명이 데이터를 거의 동시에 보내니, UDP리시버와 센더를 스레드 하나씩 쓰면, 버퍼가 쌓임
        > 그래도 스레드를 늘리면, 서버가 과부화 및 오히려 속도 저하될 수도 있으니, 일단은 단일 스레드로 써보자 (리시버 함수의 데이터 저장하는 속도를 믿어보자!)

        !!!! 서버측에서 클라이언트에게 메세지를 보내려면, 메세지를 받은 후 받은 주소가 필요함
        루트1. rerquest서버 처럼, 위치 정보를 보내면 다시 보내주는 식으로 만든다.
        루트2. 게임이 시작되면 모든 사용자들이 정보를 보내고, 거기서 주소를 따로 보관하여 스레드화 해 메세지를 보내고 받는것을 구분한다,

        이상적인 방법은 루트2의 루트2지만, 주소가 클라이언트가 메세지를 보낼 때 마다 바뀔 수 있어서 검증 필요하다.
        일단 루트1로 만들어보고, 속도 느리면 루트2로 전환.



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