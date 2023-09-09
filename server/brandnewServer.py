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
        self.whos = {} #닉네임과 핸들러를 모아놓은 딕셔너리 > 닉네임 : 핸들러
        self.mapCode = ""
        self.inGame = False
        self.roomName = roomName
        self.startPos = []
        self.mapDownloading = False
        self.whosReady = {} #닉네임 : 준비 여부
        self.udpOpen = False #현재, udp통신은 닫혀있음을 나타냄


    

    def joinRoom(self, client, addr, name):

        self.whos[name] = client #목록에서 핸들러와 아이피 추가 
        self.whosReady[name] = False #준비 목록에 추가 + 플레이어 ip가 아닌 이름을 사용하는 리스트로도 겸용한다.
        print(addr, name + "입장")
        #self.castCmd("INFO"+"!".join(self.whos.keys()), client) #접속한 플레이어 에게만, 방 인원 정보
        #self.multiCastCmd(f"IN{name}, {addr}") #플레이어들에게, 플레이어 추가 로그

    def leaveRoom(self, addr, name):
        self.whos.pop(name) #목록에서 핸들러와 아이피 지우기
        self.whosReady.pop(name, None) #준비 목록에서 이름 빼고, 오류 날시 오류대신 None반환
        #self.multiCastCmd(f"OUT{name}, {addr}")

        self.garbageCollector() #방인원이 없을때를 대비해, 인원검사시 방을 없애는 함수 실행


    def setMap(self, mapCode):
        if f"{mapCode}.dat" in os.listdir("./Maps"):
            self.mapCode = mapCode
            
            for p in self.whosReady.keys():
                self.whosReady[p] = False #맵 바뀌면, 모두 준비가 풀리게

            return "0080"
        else:
            return "0000"






    def startGame(self): #1008신호를 받았을시 처리하며, 룸 함수 mapsend를 포함한다
        #인원이 안되는건 클라이언트에서 감지한다


        self.inGame = True #방의 게임중 시그널 키기
        print("a")
        for c in self.whos.values():
            c.inGamePlayer = True #각 핸들러의 inGamePlayer신호 켜기
        # self.mapDownloading = True #하트비트 잠깐 끄기
        
        



        volatile_sendMap = threading.Thread(target=self._sendMap2Client)
        volatile_sendMap.start() #맵 전송 스레드 시작 (recv스레드와 병목되어서)



    def endGame(self):
        self.inGame = False 
        for c in self.whos.copy().values():
            c.inGamePlayer = False #각 핸들러의 inGamePlayer신호 끄기
            
        self.udpHandler.endGame()
        del self.udpHandler

    def multiCastChat(self, msg, name): #방에 있는 모든 클라이언트에게 룸챗 메세지 전송
        for c in self.whos.copy().values():
            c.sendMsg(f"roomChat!{name}:{msg}") #!로 구분, 닉네임 : 내용

    def multiCastCmd(self, msg): #방에 있는 모든 클라이언트에게 커맨드 메세지 전송
        for c in self.whos.copy().values():
            c.sendMsg("CMD " + msg)

    def castCmd(self, msg: str, target: classmethod): 
        '''
        castCmd는
        접속한 특정 ip에게 메세지 반환 
        target:핸들러자체
        '''

        target.sendMsg("CMD " + msg) 

    def garbageCollector(self):
        if len(self.whos.keys()) == 0: #방 인원이 0 명이면
            self.deleteRoom()

    def readyPlayer(self, name: str): #플레이어 준비 시키기
        self.whosReady[name] = True #어짜피 클라이언트에서 정보 요청시 준비 목록이 가기 때문에, 값만 바꾸고 바뀐값 전송 안해도 ok!

    def noreadyPlayer(self, name: str): #플레이어 준비 해제 시키기
        self.whosReady[name] = False

    def deleteRoom(self):
        roomList.remove(self) #방목록에서 삭제
        del self #자신의 참조 삭제



    def _sendMap2Client(self):
        self.errBool = False #이 함수가 실행될 때 마다 생기는 것, 방에서 이 요청은 하나 뿐이기 때문에 중첩 걱정 없다
        '''
        recv스레드와 병목이 되기 때문에, 스레드로 실행된다.
        준비가 다 될 때 게임 시작시, 가장 먼저 호출되는 클래스전용 함수
        맵파일을 전송하고 관리하며, 오류가 나면 거의 다 방에서 나가게 하기에,
        이 함수를 거치고 udp통신을 할때 인원수를 다시 보낸다.
        
        !!중요!! 여기서 udp통신을 연다.
        
        '''
        '''
        print("udp연결")

        globals()["udp-" + self.roomName] = udpGame(self.whosReady, self, f"udp-{self.roomName}")

        self.udpHandler = globals()["udp-" + self.roomName]

        globals()["udp-" + self.roomName].start() #udp 통신 실행 정보 udp소켓과 tcp 소켓은 분리되어있다!
            
        print("udp 포트 열기 완료")
        '''

        for c in self.whos.copy().values(): #핸들러들에게, mapSend실행
            print(c)
            print("핸들러 맵 보내기 시작")
            
            res = c.sendMapfile(self.mapCode) #sendMapfile은 파라미터에 맵코드가 들어간다

            print("결과 나옴", res)

            if res == "OK": #성공인 경우
                pass #클라이언트는, 다른 플레이어가 for문을 돌때 까지 대기한다
            else: #실패인 경우
                self.errBool = True
                break #포문 중단



        if not self.errBool: #성공인 경우
            #UDP연결 열기
            #TCP로 UDP연껼 씨짞 뽀냬끼
            print("연결 성공 확인돔")
            self.udpOpen = True #udp소켓열림, udp핸들러가 존재함을 알려준다
            self.udpHandler = udpGame(self.whos.keys(), self, f"UDP-{self.roomName}") #객체 선언, 자동으로 열어진다(스레드라서)
            print("udp열었고, 알림 보냄")
            self.multiCastCmd("UdpOPEN") #udp열림 보내기 (클라이언트 대기 해제)
            
            sys.exit() #스레드 종료




        else:
            self.multiCastCmd("ERR2GET") #ERR메세지 전송 클라이언트는 받으면 방에서 나간다.
            time.sleep(2) #다 나가는 것 대기
            self.deleteRoom() #방 지우기
        

            sys.exit() #스레드 종료


            '''

            if res == "FAIL": #맵 다운 중 실패한 경우(클라이언트 측에서)
                globals()["udp-" + self.roomName].clientAddr.pop(c.name)
                globals()["udp-" + self.roomName].clientPos.pop(c.name) #udp소켓 목록에서 플레이어 제거
                c.leaveRoom() #클라이언트의 방 나가기 실행
                self.mapDownloading = False #하트비트 켜기
            elif res == "SOMETHING ERROR": #다운 중 뭔가 오류가 일어난 경우
                self.castCmd("smterr", c)
                globals()["udp-" + self.roomName].clientAddr.pop(c.name)
                globals()["udp-" + self.roomName].clientPos.pop(c.name) #udp소켓 목록에서 플레이어 제거
                c.leaveRoom() #오류 메세지 전송하고, 방에서 내보내기
                self.mapDownloading = False #하트비트 켜기

            elif res == "NOFILE": #서버에 맵 파일이 없는 경우
                self.castCmd("nofile", c)
                self.mapDownloading = False #하트비트 켜기
                pass #이경우는, 그냥 다시 시도하면 되는 것이기에 다시 화면으로 돌아가깅

            else: #다른 문제다 그러면 그냥 넘겨도 되기에, 0080전송
                
                self.castCmd('0080', c)
                print("끝나사 udp 통신 시작하라는 0080 전송 하기")
                self.mapDownloading = False #하트비트 켜기
            
        sys.exit() #스레드 종료

        '''

class Handler(): #각 클라이언트의 요청을 처리함 스레드로 분리!, TCP
    def __init__(self, soc, addr):
        self.soc = soc
        self.inRoom = False
        self.inGamePlayer = False
        self.addr = addr[0]
        self.name = "" #플레이어 닉네임
        self.inEditor = False #에디터화면 일때
        self.alive = True
        self.howAlive = 3 #최대 몇번까지 봐줄건가
        self.msg = ""

        self.run() #시작 함수는 모든 변수 설정 후 마지막에 호출!!
        
        

    def run(self): #시작
        
        heatBeatThread = threading.Thread(target = self.heartBeat) #하트비트 시작
        heatBeatThread.start()
        recvThread = threading.Thread(target=self.recvMsg) #받기 시작
        recvThread.start()
        


    def shutDown(self): #종료
        
        self.soc.close()
        
        if not self.inEditor:
            players.remove(self.name)
            
            
        print("shutdown the thread")
        del self

    
    def heartBeat(self): #클라이언트의 접속 끊어짐을 확인하면, 데이터를 지우고 소켓을 닫는다
        
                
        self.heartStack = 0
        while self.heartStack <= self.howAlive:
            time.sleep(10) #10초간격으로, 스레드 안에서 진행이라 논 블락킹이다! ㅎㅎ
            try:
                print("")
                self.heartStack += 1
                self.sendMsg("7777") #7777이라는 heartbeat 신호 보내기 
                    
            except: #오류 발생시 그냥 보내버리기
                break

            if self.heartStack > self.howAlive:
                break

        if self.inRoom: #방에 있을 때는
            self.inRoom = False
            self.roomHandler.leaveRoom(self.addr, self.name) #방 핸들러에서 자신의 정보 제거
            del self.roomHandler #조심 del 함수는 참조를 없애는거기 때문에, 룸 핸들러가 없어지는게 아님
                #룸 핸들러의 참조가 모두 사라지면, 파이썬의 garbage collector가 자동으로 룸 핸들러를 삭제시킴


        elif self.inGamePlayer: #게임 중 (UDP 통신 중일 시에는)
            self.roomHandler.gameHandler.connDown(self.name) #해당 방 udp핸들러의 connDown 실행(udp 통신 중에서 제거 하는 것)
            del self.roomHandler

        else:
            print("아무것도 아닌... 하트비트 내용")
            

        self.shutDown() #연결 종료
        sys.exit() #현재 스레드 종료     

            


    def makeRoom(self, roomName): #방 생성
        if roomName not in roomList:
            globals()["room" + roomName] = Room(roomName) #roomroomName의 변수 명으로 Room 클래스 선언(방을 팜)
            roomList.append(evaler(roomName)) #방 목록에 append, eval은 roomroomName을 호출하는 함수로, 클래스를 반환 함 즉, roomList엔 방이름의 인스턴스들이 있다.
            self.sendMsg("0080") #방 만들기 성공
            print("방 만들기 성공")
        
            return self.joinRoom(roomName) #방 이름만 문자열로 보낸다

        print("방 제작 실패")
        return False

    def joinRoom(self, roomName):

        roomName = evaler(roomName) #evaler는 여기서 적용한다

        if roomName in roomList:
            if len(roomName.whos.keys()) < 4: #방 인원이 4명 이내일 때만
                roomName.joinRoom(self, self.addr, self.name) #self는 클래스 자신을 의미, 즉 현재 핸들러를 보내려면 자기자신 self를 보낸다.
                self.inRoom = True
                self.roomHandler = roomName #클래스에 핸들러 설정
                return True
            
            else:
                return False

        return False
    

    def leaveRoom(self):
        print("leaving room..")
        self.inRoom = False
        self.inGamePlayer = False #방 상태 전부 해제
        self.roomHandler.leaveRoom(self.addr, self.name) #방 핸들러에서 자신의 정보 제거
        del self.roomHandler #조심 del 함수는 참조를 없애는거기 때문에, 룸 핸들러가 없어지는게 아님
            #룸 핸들러의 참조가 모두 사라지면, 파이썬의 garbage collector가 자동으로 룸 핸들러를 삭제시킴
        
        return True


    def checkRoom(self):
        print("checkroom")
        result = '!'.join(f"{x.roomName},{len(x.whos.keys())}" for x in roomList)#roomList를 문자열로 '!'를 사용하여 구분하여 문자열로 만듬 , + 메모리 절약으로 실행속도 개선
        if result:
            return result #결과 값 반환.
        else:
            return "NULL"

    def recvMsg(self): #클라이언트로 부터의 메세지 수신 핸들러    조심! self파라미터에는 힌트 (: 속성) 작성 금지!, vscode에서 함수 내 코드가 힌트를 못 불러온다,
            
            

            while True:
                data = self.soc.recv(1024).decode()


                while data == "" and len(data) == 0: #데이터 도착까지 기다리기
                    data = self.soc.recv(1024).decode()
                    pass

                self.msg = data

                print(self.msg)


                
                


                


                
                # elif self.msg == "0000" or self.msg == "1111":
                #     print("제발...")
                #     self.tempData = self.msg
                if not self.msg == "7780": 
                    # print(f"{datetime.now()} :  {self.addr}")
                    

                    # print(self.msg)

                    # if self.msg == "7777": #heartBeat 신호
                    #     self.alive = True #요청보내면 살아있다 표시
                    #     self.soc.send("0080".encode())
                        

                    
                    if self.msg == "9999": #연결 종료 사안
                        self.msg = ""
                        self.shutDown()
                        sys.exit() #현재 스레드 종료

                        #테스트

                    







                    elif "2000" in self.msg: #에디터 통신일 때
                        self.inEditor = True
                        reqMap = self.msg.replace("2000CODE", "") #2000을 보냈으면, 맵 코드를 보낸다.
                        print("이게 맵 " + reqMap)
                        
                        print(os.listdir("./Maps/"))
                        if reqMap+".dat" in os.listdir("./Maps/"): #!로 구분된 문자열이 출력이라, 변환해야 함
                            
                                print("0000 전송")
                                self.sendMsg("0000") #이미 존재
                                self.msg = ""

                        else:
                            print("0080전송")
                            self.sendMsg("0080") #전송시작.
                            
                            with open(f"./Maps/{reqMap}.dat", "w") as f: #파일 읽어서 저장 시작
                                print("파일 읽기")
                                try:
                                    print("2")
                                    stream = self.soc.recv(1024).decode() #먼저 1024를 읽는다.
                                    print(bool(stream))
                                    end = False
                                    while not end: #EOF명령을 받으면, 쓰기 종료
                                        f.write(stream) #stream 쓰기
                                        print("받아오는중,,,")
                                        print(stream)
                                        if stream.strip()[-1] == "*": #마지막 문자가 *이면 (종료면)
                                            end = True #종료
                                            stream = 0
                                        else:
                                            stream = self.soc.recv(1024) #다시 1024만큼 읽는다. 이런 순서로 하면, 코드가 단축화 된다.
                                            stream = stream.decode()
                                    print("완료")
                                    f.close() #파일 저장
                                    self.sendMsg("0080") #성공 메세지 전송
                                    print("완료 전송")
                                    print("소켓 닫기")
                                    self.msg = ""
                                    self.soc.close() #소켓 닫기
                                    break

                                except Exception as e:
                                    self.sendMsg("0000") #오류 메세지 전송
                                    print(e)
                                    self.msg = ""
                                    self.soc.close() #소켓 닫기
                                    break

                    if not self.inRoom: #방 목록 탐색기에 있을때.
                        if self.msg == "0010":
                            print("ok")
                            self.msg = ""
                            self.sendMsg("0080") #OK sign   
                        elif "0001" in self.msg: #이름 설정, 수신 형식 0001이름    ex) 0001ADEL
                            print("0001수신, 이름")
                            if not self.msg.replace("0001", "") in players:
                                self.name = self.msg.replace("0001", "") #잘라내기 이름 설정
                                players.append(self.name) #플레이어 목록에 이름추가


                                self.msg = ""
                                self.sendMsg("0080") #OK sign

                            else:

                                self.msg = ""
                                self.sendMsg("0000")
                        elif self.msg == "0002": #방 목록 수신
                            result = self.checkRoom() #함수값이 룸 리스트, 형식은 !로 구분함  ex)roomna!jai123!kurukuru!bang
                            
                            self.msg = ""
                            self.sendMsg(result)

                        elif "0003" in self.msg: #방 만들기 수신 형식은 0003방이름
                            self.makeRoom(self.msg.split('3')[1])
                            #0080 수신은, 방 join하면 방목록을 보내버려서, 그 전에 보내긱 위해, makeRoom 안에존재.

                            self.msg = ""
                        elif "0004" in self.msg: #방 입장 수신 형식 0004방이름

                            roomName = self.msg.replace("0004", "") #잘라내기 이름 설정

                            res = self.joinRoom(roomName)
                            if not res:
                                self.sendMsg("0000")
                            
                            else:
                                self.sendMsg("0080") #OK sign

                            self.msg = ""
                                






                    else: #방 목록 탐색기가 아닐 때 (방 안 or 게임 중)
                        if self.msg == "0002": #방 목록 수신
                            result = self.checkRoom() #함수값이 룸 리스트, 형식은 !로 구분함  ex)roomna!jai123!kurukuru!bang
                            self.sendMsg(result)
                            self.msg = ""
                        
                        # 디버그






                        elif self.msg == "1000": #맵 목록 조회
                            print("맵 view")
                            self.sendMsg(checkMapList())
                            self.msg = ""
                        elif "1001" in self.msg: #맵 설정 형식 >> 1001!MapCode >>0080 송신
                            mapCode = self.msg.split("!")[1]
                            self.sendMsg(self.roomHandler.setMap(mapCode)) #setMap 성공 여부에 따라 메세지 보내주기
                            self.msg = ""
#1002는 명령 중복으로 삭제됨

                        elif self.msg == "1003": #방 나가기

                            if len(self.roomHandler.whos.keys()) == 1: #1명일때
                                self.roomHandler.deleteRoom() #삭제 요청
                                del self.roomHandler #핸들러 참조 삭제
                                self.inRoom = False
                                self.sendMsg("0080")
                                self.msg = ""

                            else:
                                if self.leaveRoom():
                                    self.inRoom = False
                                    self.sendMsg("0080")
                                    self.msg = ""
                                else:
                                    self.sendMsg("0000")
                                    self.msg = ""
            

                        elif self.msg == "1004": #방 파쇄 (플레이어가 1명 밖에 없을때만 가능)
                            if len(self.roomHandler.whos.keys) == 1:
                                self.roomHandler.deleteRoom() #삭제 요청
                                del self.roomHandler #핸들러 참조 삭제
                                
                                self.inRoom = False
                                self.sendMsg("0080") #완료메세지
                            else:
                                self.sendMsg("0000")

                            self.msg = ""

                        elif self.msg == "1005": #방 정보 요청
                            self.sendMsg(self.sendRoomInfo())

                            self.msg = ""
                        elif self.msg == "1006": #준비 sign
                            self.roomHandler.readyPlayer(self.name)

                            



                            self.msg = ""
                        elif self.msg == "1007": #준비 해제 sign
                            self.roomHandler.noreadyPlayer(self.name)
                    
                            self.msg = ""


                        elif self.msg == "1008": #게임시작준비 요청 (맵 다운 > udp연결)
                            print("b")
                            self.msg = ""


                            self.roomHandler.startGame() #요청, 이 함수가 끝나기 전까지 recvMsg 함수는 사용 불가

                            #이놈을, 1008 이내에서 실행해버리면, 끝나ㅣ 전까지 recv가 다시 한번 호출이 안됨.
                            print("startGame 끝")
                            
                            pass

                        elif self.msg == "mapOk": #맵 수신 완료를 받으면
                            self.mapSign = "ok" #맵 사인 ok 변경 (항상 보낼때마다, no이고 계속 no이면 타임아웃으로 간주하고 연결 실패)

                        elif "READY2GET" in self.msg:
                            self.tempRes = "READY2GET"
                            print("tmepres넣었음")
                        elif "ALREADYMAP" in self.msg:
                            self.tempRes = "ALREADYMAP"




                        print(self.msg)

                    
                else: #hearbeat 신호일시
                    print("heartISBumping")
                    self.heartStack = 0
                    pass
                

                print("recv 진행중")
                            

                                



                        
                                    




    def sendMapfile(self, mapCode: str): #return이 문자열이라, 실행시 인스턴스처럼 실행시키고 조건문으로 결과비교 필요   맵 파일을 클라에게 전송
        
        self.tempRes = ""
        
        self.soc.send(f"1008{mapCode}".encode())

        while not (self.tempRes == "READY2GET" or self.tempRes == "ALREADYMAP"):
            pass



        if self.tempRes == "READY2GET": #이 메세지 받을 시
            self.msg = ""
            print("맵이 존재하지 않음 >> 다운받기 시작")

            with open(f"./Maps/{mapCode}.dat", 'r') as f:
                try:
                    self.mapSign = "no" #기본값 no (클라이언트가 맵을 잘 받으면 mapOk로 바뀜)

                    data = f.read(1023) #1023바이트 읽기
                    while data: #data가 없어질 때 까지
                        self.soc.send(f"^{data}".encode()) #1023 크기의 맵 파일앞에 ^붙여서 전송
                        print(len(data), '전송함')
 
                        time.sleep(0.5) #0.5초 정도 받는 것 기다림
                        if self.mapSign == "no":
                            
                            time.sleep(1) #1초 더 기다림(1번 기회)
                        if self.mapSign == "no":
                            return "FAIL" #실패 반환
                        
                        self.msg = "" #메세지 초기화
                        self.mapSign = "no"
                        print("맵 데이터 다시 전송")
                        data = f.read(1023) #그 다음 데이터 읽기


                    return "OK" #성공 반환
                
                    #클라이언트는, 나머지 for문으로 다른 사람이 이 행위를 성공할때 까지 대기 + 화면에 다른 플레이어 준비중을 띄움
                    #for문 바깥에, braodcast를 사용해, 클라이언트가 특정 메세지를 감지하면 대기가 풀리는 형식


                except Exception as ex: #서버가 읽는 것에 오류가 날시에
                    print(ex)
                    return "FAIL"
                
        
        elif self.tempRes == "ALREADYMAP": #이미 맵이 존재할 시     
            self.msg = ""   
            return "ALREADY" #맵 존재 시그널 반환
        
        
        else:
            print("이상한 신호")
            print(self.msg)

        '''
        
        전 버전
        
        
        
        
        if f"{mapCode}.dat" in os.listdir("./Maps/"): #보낼 파일이 존재하지 않으면, 안되게 False전송
            
            
            self.tempData = "" #메세지 초기화
            print("맵 요청 시작")
            self.soc.send(f"1008{mapCode}".encode()) #맵 요청
            print("맵 요청 보냄")
            
            while not self.msg == "1111" and not self.msg == "0000":
                pass




            # data = self.soc.recv(1024)
            # self.tempData = data.decode()

            # print(self.tempData)

            if self.msg == "0000": #클라이언트가 맵이 있대!!
                print("클라가 맵이 있다는데")
                return "ALREADY" #이 경우는 , 무시한다 (바로 udp로 통신을 받기 때문에)


            elif self.msg == "1111": #클라이언트가 맵이 없다고 함! > 전송요청

                print("전송 시작")
                with open(f"./Maps/{mapCode}.dat", 'r') as f:
                    print("맵 열기")
                    try:
                        mapData = f.read(1023) #파일에서 1000바이트 씩 읽기, 나머지 1바이트는 맵 파일임을 알리기 위해 추가할 문자(^)다!
                        print("맵 읽음")
                        while mapData: #data가 0 (다 읽을 때 까지), 이렇게 하는 이유는 1024바이트 씩 읽고, 없어질때를 더 효과적으로 표현 가능
                            #만약 while이 없었으면 f.read(1024)를 for문으로 돌려야 했다.
                            print(len(f"^{mapData}"))
                            self.soc.send(f"^{mapData}".encode()) #1024 크기의 데이터를 보낸다, 참고 - 소켓의 send함수는 리턴이 보낸 데이터의 크기를 봔환
                            #이러면 보낼때마다 ^맵파일 내용으로 보내, 클라이언트 측에서는 이를 구분하여 저장함
                            print(mapData)
                            
                            while not "mapOk" in self.msg: #mapOk사인을 받기 전까지 대기, 받아야 다음걸 전송한다, 격주 > mapOK가 중복되는 경우가 존재 따라서, 포함으로 감지한다.
                                #print(len(self.msg))
                                pass
                            mapData = f.read(1023) #다시 1024만큼 읽어본다.
                            print("mapOkk받았서")
                            self.msg == "" #받으면, 메세지 초기화
                            

                        while True: #클라이언트에서 성공 혹은 실패 메세지가 올때까지, 대기
                            print("받음", self.msg)
                            if self.msg == "0080": #성공메세지 수신시
                                print("OK")
                                return "OK" #이 경우는 , 무시한다 (바로 udp로 통신을 받기 때문에)
                            elif self.msg == "0000":
                                print("FAIL")
                                return "FAIL" #이경우는, 이 함수를 실행한 곳에서, 플레이어 퇴출


                    except Exception as ex:
                        print(f"전송 중 오류 : {ex}")
                        return "SOMETHING ERROR" #오류메세지와 true출력, 이 함수를 실행한 곳에서, 플레이어 퇴출
    
                
            else:
                return "NOMSG"
                pass #아무 메세지도 아닌경우
            
            
        else: #서버에 그러한 파일이 없으면
            print("파일이...없다!")
            self.soc.send("NOFILE".encode())
            return "NOFILE" #이경우는, 플레이어들에게 맵 파일 없다고 전송ㅂ


            '''

    def sendMsg(self, msg: str):
        self.soc.send(msg.encode())
        return True


    def sendRoomInfo(self):
        #방이름, 방 플레이목록, 맵 코드, 플레이어 준비현황(맵 다운됐을 때 준비가능), 게임시작여부
        
        '''
        클라이언트 측에서, 1초 간격으로 방 정보를 요청함
        
        형식 : ROOMINFO방이름!플레이어목록(리스트 형식 str)!맵 코드(없으면 None)!플레이어 준비 현황({플레이어 : True or False}을 문자열로 )!True or False
        '''


        infoData = f"CMD ROOMINFO{self.roomHandler.roomName}!{str(list(self.roomHandler.whosReady.keys()))}!{self.roomHandler.mapCode}!{str(self.roomHandler.whosReady)}!{self.roomHandler.inGame}"
        print(infoData)
        return infoData
        #.keys()는 dic_list객체라, list로 만들고 다시 문자열 str로 감싸야 함




   # def run(self):
        #msgRecv = threading.Thread(target = self.recvMsg, args = (self,)) #메세지 받는 스레드 시작 (스레드는 개별 객체라 self를 보내줘야 함)
        #msgRecv.start()
    #    self.recvMsg()


    
def checkMapList():
    result = '!'.join([x[:-4] for x in os.listdir("./Maps/")]) #Maps 디렉토리의 맵 파일 이름들을 가져와 문자열로 만들기, 뒤에 .dat은 빼준다
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












class udpGame(threading.Thread):
    '''
    인 게임에서 정보를 주고 받을 udp소켓
    클래스 자체가 스레드화 됨.
    '''
    


    def __init__(self, clientsName: list, room: Room, threadName: str): #clientsName : 참여자들 닉네임 '리스트', room : 방 핸들러, threadName : 스레드 이름

        super().__init__() # 상위 클래스 초기화(상위 클래스의 메소드를 가져온다)

        self.name = threadName #스레드의 이름을 지정한다, (self.name >> 상위 클래스인 threadingThread의 메서드)


        self.room = room #udp가 실행된 room 방 객체를 가져온다.
        self.clientPos = {} #플레이어들의 위치 값
        self.clientAddr = {} #접속 한 클라이언트의 아이피주소와 포트의 튜플 값 key:닉네임, value : 튜플
        self.rgb = [0, 0, 0] #rgb 값 저장할 리스트
        self.change = self.rgb #rgb의 변화량 감지 리스트
        self.readyStack = 0 #준비 인원수 (방 인원수 만큼 되면 게임이 시작됨, 준비는 초기화 메세지를 보내면 스택 +1)
        self.done = False #스레드의 while문을 종료시킬 원격 함수
        for c in clientsName:
            self.clientPos[c] = "0, 0" #클라이언트  이름: "x, y" 위치정보를 저장
            self.clientAddr[c] = ("", 0000) #주소값 초기화
        


       
        

    def run(self):
        '''
        thread클래스에 의해 자동으로 실행되는 것
        '''


        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #소켓 재사용 키기
        self.udpSock.bind((HOST, PORT)) #클래스 인스턴트를 만들면 udp소켓 열기
        print("udp game server listening")

        volatile_standingBy = threading.Thread(target=self.standingBy)
        volatile_standingBy.start() #플레이어 준비 받기


    def standingBy(self): 
        '''
        !!스레드 1개사용, 게임 시작시 스레드 종료시킴!!
        가장 먼저 실행되고, 플레이어가 모두 준비 되면, 신호를 보내고 리시브와 센드 메세지의 스레드를 실행한다.
        처음 플레이어들에게서 준비가 되면, 초기화 메세지(기본 위치, 클라이언트 주소)를 받는다.
        '''

        #준비 메세지 : S이름!기본좌표
        while True:
            msg, fromAddr = self.udpSock.recvfrom(1024)
            msg = msg.decode()
            
            while msg == None or msg == "": #공백이거나 없는 값(읽지 못 하면) 다시 불러온다
                msg, fromAddr = self.udpSock.recvfrom(1024)
                msg = msg.decode()



            if msg.startswith("S"):
                msg = msg.replace("S", "").split("!") #!기준으로 나누기
                self.clientAddr[msg[0]] = fromAddr #플레이어 주소 저장
                self.clientPos[msg[0]] = msg[1]
                self.readyStack += 1 #준비 인원 +!

                self.udpSock.sendto("0080".encode(), fromAddr)

            else:
                self.udpSock.sendto("0000".encode(), fromAddr)

            if self.readyStack == len(self.clientPos.keys()): #모든 인원들이 준비가 된다면.
                self.room.inGame = True
                self.startGame()
                break
                

        sys.exit() #스레드 종료 시키기



    
    def recvMsg(self): #클라이언트로의 메세지를 분별 및 확인하여 전송
        while not self.done: #self.done (boolean)값은, 게임이 종료될때, True가 된다.   
            msg, fromAddr = self.udpSock.recvfrom(1024)
            msg = msg.encode()
            msg = msg.split('!') #!로 구분함  >  형식 : P방이름!위치정보!이름
                                # RGB변경시 메세지 > 형식 : R방이름!R,G,B!이름
                                #게임 종료 메세지 > @!
            #방 이름이 없는데 요청한경우 오류가 나기 때문에.


            if msg[0][1:] == self.room.roomName: #해당 방이름의 요청에만 응답!   msg[1] > P방이름 or R방이름 , msg[1:] >> R과 P (앞글자가 사라짐)
                if msg[0][0] == "R": #RGB변경 메세지 일때     msg[0][0] >> 슬라이스 된 값의 앞글자 한글자
                    self.rgb[0] = msg[1].spilt(',')[0]
                    self.rgb[1] = msg[1].spilt(',')[1]
                    self.rgb[2] = msg[1].spilt(',')[2] #Rgb정보 저장

                elif msg[0][0] == "P": #위치정보 저장 (거의 대부분 이게 요청 됨.)
                    self.clientPos[msg[2]] = msg[1]
                elif msg[0] == "@":
                    self.room.multiCastCmd("GAMEOUT") #TCP모듈에 게임 끝 선언
                    self.endGame()
    
        self.endGame()
        sys.exit(0) #self.done 이 켜지면 스레드 종료

    def sendMsg(self): #스레드 1개 사용
        while not self.done: #self.done (boolean)값은, 게임이 종료될때, True가 된다.       

            if self.change == self.rgb: #rgb값이 변하지 않았을 때는, 위치정보만 전달.  >>위치정보는 P로 시작, RGB는 R로 시작
                for c in self.clientAddr.keys(): #이름들을 c에 담아서 반복
                    for t in self.clientAddr.keys():
                        self.udpSock.sendto(f"P{c}!{self.clientPos[c][0]}, {self.clientPos[c][1]}", self.clientAddr[t])
                        #{self.clientPos[c][0]} : x 값, {self.clientPos[c][1]} : y 값 / self.clientAddr[c] = 보낼 사람의 주소



            else:
                #rgb의 값을 클라이언트에게 전송 + 그 후 위치정보도 같이 전달
                self.change = self.rgb
                res = ",".join(self.rgb)
                for c in self.clientAddr.keys(): #이름들을 c에 담아서 반복
                    for t in self.clientAddr.keys():
                        self.udpSock.sendto(f"P{c}!{self.clientPos[c][0]}, {self.clientPos[c][1]}", self.clientAddr[t])
                        #사람 한명당 4명의 위치 정보가 필요하니 2중for문
                        #{self.clientPos[c][0]} : x 값, {self.clientPos[c][1]} : y 값 / self.clientAddr[c] = 보낼 사람의 주소
                    self.udpSock.sendto(f"R{res}".encode(), self.clientAddr[c]) #RGB값은, 플레이어 당 한명씩이니 1중 for문에
        
        self.endGame()
        sys.exit(0) #self.done 이 켜지면 스레드 종료


    
    def startGame(self):
        
        udpRecv = threading.Thread(target=self.recvMsg)
        udpSend = threading.Thread(target=self.sendMsg) #스레드 세팅

        self.room.multiCastCmd("5555") #플레이어들에게 tcp로 CMD 5555를 보낸다
            

        udpRecv.start()
        udpSend.start() #스레드 시작


    def endGame(self):
        self.done = True
        self.udpSock.close()

        del self


    def connDown(self, targetC): #플레이어 연결이 예상치 못하게 끊켰을 때 목록에서 지우는 것
        self.udpSock.close()
        print("소켓 닫음")
        self.clientAddr.pop(targetC)
        self.clientPos.pop(targetC)

        self.udpSock.sendto(f"S{targetC}", self.clientAddr[targetC])


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