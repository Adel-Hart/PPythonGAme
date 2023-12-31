import main
import pygame
import editor
import ctypes
import re
import time

#요 아래는 서버용
import os
import socket
import threading
import selectors
import sys

import logging


with open("../server/serverip.txt","r") as f:
    HOST = f.readline()
PORT = 8080

logger = logging.getLogger(name='MyLog')

logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('debug.log', encoding='utf-8')
logger.addHandler(file_handler)




inEditor = False # 에디터를 하고있는지

connected = False #서버 연결 여부

joinedRoomName = "" #현재 접속중인 방의 이름

choosedMultiMap = False #멀티에서 맵을 고를 시 True로 바뀜, 다시 방 화면으로 ㄱㄱ

roominfo = False

sel = selectors.DefaultSelector() #셀렉터 초기화


def darkColor(color): #색을 더 어둡게 
    return list(map(lambda x: x / 2, color)) #RGB 값을 모두 절반으로

class conTcp():
    def __init__(self):
        self.players = []
        self.data = ""
        self.mapStream = "" #하나의 리시브로 작동하기때문에, 맵 전송 내용이 담길 변수다.

        self.startGame = False #모든 준비가 끝나, udp통신을 시작하라는 트리거

        self.wating = False
        self.isudp = False



    def run(self): #연결 실행함수

        self.tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #소켓 생성

        try:
            print("연결 시작")

            self.tcpSock.connect((HOST, PORT)) #연결 시작, 요청을 보내고 계속 대기

            print("연결 성공")
            

            return True #연결 되면, 연결 됨 표시


        except: #연결 실패시
            print("연결 실패!")
            return False #연결 실패시, 연결 실패 표시


    def setName(self, nickName): #메세지를 받는 핸들러

        self.tcpSock.send(f"0001{nickName}".encode())

        while self.data == "":
            pass #기다리기


        print("이름 설정 중")
        print(self.data)
        if(self.data == "0080"):
            print(self.data)
            self.data = "" 
            self.nickName = nickName
            return True #성공 메세지 받을 시
        else:
            self.data = "" 
            return False
    
    def checkRoomList(self):
        self.tcpSock.send("0002".encode()) #룸 리스트 받기 형식 > ROOMLIST방이름!방이름!
        while self.data == "":
            pass #기다리기

        if self.data == "NULL":
            self.data = "" 
            return ["*EMPTY*"]
        else:
            temp = self.data
            self.data = "" 
            return temp.split("!")


    def makeRoom(self, roomCode: str): #방 만들기 (서버 상에서 자동으로 방 참여가 된다.) 이름 규칙 : 12자 내외 영문만
        self.tcpSock.send(f"0003{roomCode}".encode()) #방 생성 요청


        while self.data == "":
            pass #기다리기
        if(self.data == "0080"):
            self.data = "" 
            return True #성공 메세지 받을 시 >> 클라이언트 측 핸들러에서, 룸 용 함수 실행 필요
        
        else:
            self.data = "" 
            return False
            
        
    def joinRoom(self, roomCode: str): #방 참여요청

        print(roomCode)
        self.tcpSock.send(f"0004{roomCode}".encode()) #방 입장 요청

        while self.data == "":
            pass #기다리기:

        
        
        if(self.data == "0080"):
            global joinedRoomName
            joinedRoomName = roomCode
            print(roomCode, self.data)

            self.data = ""
            return True #성공 메세지 받을 시
        
        
        else:
            self.data = ""
            return False
    
    def setMap(self, mapCode):
        self.tcpSock.send(f"1001!{mapCode}".encode()) #맵 설정 요청

        while self.data == "":
            pass #기다리기
        
        if(self.data == "0080"):
            print(f"맵코드설정:{mapCode}")
            self.data = "" 
            return True #성공 메세지 받을 시
        else:
            print("맵코드 실패?", self.data)
            self.data = ""
            return False

    def leaveRoom(self):

        self.tcpSock.send("1003".encode()) #방 나가기 요청
        
        while self.data == "":
            pass #기다리기

        if(self.data == "0080"):
            print("나가기 완료")
            global joinedRoomName
            joinedRoomName = ""
            self.data = ""
            serverRoomList(self, 1) #방 목록 다시 불러오기
            return True #성공 메세지 받을 시
        else:
            print("나가기 실패")
            self.data = ""
            return False



    def inRoom(self): #방에 접속시 실행됨, 송신 스레드와 수신 스레드가 실행됨
        return






    '''
    받는 명령어 핸들러를 스레드로 작동시키고, 방 정보 가져오는 건 핸들ㄹ러에서 처리하고, 각자 함수를 가져 스레드를 켜논 동시에
    데이터를 받아와야 하는 명령을 할시에 전역 변수 threadOn을 꺼서, 스레드에서 명령어를 가져오는걸 잠시 멈추게 한다.

    또는

    핸들러에서 받는 메세지를 전역변수화 시켜서, 함수에서 가져오는 것이다. <이게 좀 더 괜찮은 듯?  < 8/29 채택

    
    
    
    '''
    def recvRoom(self): #받는 명령어 핸들러 스레드
        self.data = ""
        self.cmd = ""
        while True:

            recvMsg = self.tcpSock.recv(1024).decode()

            if recvMsg == "7777":
                print("7777전송")
                if joinedRoomName == "": #서버가 보낸 heartBeat신호일 시
                    self.tcpSock.send("7780".encode()) #응답하기


        

            elif recvMsg.startswith("1008"):
                mapCode = recvMsg.replace("1008","")
                print("맵큐드",mapCode)


                settingGame = threading.Thread(target=self.setGame, args=(mapCode, )) #
                settingGame.daemon = True
                settingGame.start() #게임 준비 스레드 작동하기!


            elif recvMsg.startswith("CMD"): #CMD로 시작되는, 서버 설정 메세지인 경우
                
                self.cmd = recvMsg.replace("CMD ", "")

                logger.debug(self.cmd)

                if self.cmd == "UdpOPEN": #위에서 실행되고, 여기서도 실행
                    print("UDP오픈 메세지 수신")
                    self.startGame = True #1008수신때, False로 초기화됨


                elif self.cmd == "ERR2GET":
                    #오류 발생
                    print("맵 가져오는데 오류 발생")


                elif self.cmd == "5555":
                    print("5555수신함")
                    time.sleep(1)
                    self.udpPlay.startGame = True #udp설정 끝, udp게임시작 통신 개시    

                    
                elif self.cmd == "okUDP":
                    self.udpPlay.initCon = True #세팅 성공 트리거 작동, 기본값은 False이며 udpPlay만들때 초기화 됨

                elif self.cmd == "ENDGAME":
                    self.wating = False
                
                elif "QUITGAME" in self.cmd:
                    who = self.cmd.split("!")[1]
                    if self.nickName == who: #자기 자신이 나가는 요청이면
                        
                        pass
                    else:
                        self.udpPlay.outPlayer(who)
                
                    
                    
                    
                    




            elif recvMsg.startswith("^"): #맵인 경우에
                logger.debug(self.mapStream)
                #대충 맵 내용 변수에 저장하는 내용
                #아마 self.stream
                
                if recvMsg != self.mapStream: #새로운 것을 수신 했을때,
                    if self.mapStream == "": #새로운 것을 받을 준비가 된거면,
                        self.mapStream = recvMsg #읽은 값을 저장한다.
                        logger.debug("새로운 값을 저장")
                    
                    else: #아직 맵파일 쓰고 있는데, 요청이 들어왔던거면,
                        while not self.mapStream == "":
                            logger.debug(f"not yet :{self.mapStream}")
                            pass #맵파일 다쓰고, 요청을 받을 때까지 대기, 파일쓰는게 많이 느린게 아니라, heartbeat에 걸리지 X
                        self.mapStream = recvMsg
                        logger.debug("새로운 값을 저장")

                else:
                    logger.debug("새로운 것을 수신하지 않음")


            

            else:
                logger.debug(f"못 받은 메세지 : {self.data}")
                self.data = recvMsg
                
            
            # else:
            #     #self.data = "" #서버가 맵 정보를 받는 중이기 때문에 거의 모든 작업 보류
            #     pass
            





        #서버 메세지 필터링
        

    
    
    def getRoomInfo(self):
        '''
        방정보를 불러옴
        0 : 방이름
        1 : 플레이어 리스트 형식의 str
        2 : 맵 코드 (없으면 None)
        3 : 플레이어 준비 현황 {플레이어 : True}
        4 : 게임 시작 여부 - True or False
        '''
        global roominfo

        while joinedRoomName != "":
            for i in range(10):
                print("getroominfo 순항중!")
                self.tcpSock.send("1005".encode()) #방 정보 요청
                
                
                if self.cmd.startswith("ROOMINFO"): #ROOMINFO로 시작하는 방 정보 메세지 일때
                    roomIf = self.cmd.replace("ROOMINFO", "")
                    roomIfList = roomIf.split("!")
                    self.cmd = ""
                    roominfo = roomIfList
                    

                    #형식 ROOMINFO방이름!플레이어목록(@로 구분)!맵 코드(없으면 None)!플레이어 준비 현황({플레이어 : True or False}을 문자열로 )!True or False

                        #del data #변수 참조 삭제,  받는 변수로 바뀌어서 삭제하면 안된다.
                        
                        #return True #성공 메세지 받을 시 <<어짜피 실행 안될텐데
                    
                else: #무효일시
                    pass

                time.sleep(1)

                if joinedRoomName == "":
                    print("getroominfo 탈출")
                    break

            self.tcpSock.send("7780".encode()) #하트비트 대신 보내기

        sys.exit()
        
    def getMapCodeList(self):
        self.tcpSock.send("1000".encode()) #맵코드 목록 요청

        while self.data == "": #데이터 도착까지 기다리기
            pass
        
        mapCodes = self.data.split("!") #맵 코드로 된 리스트 생성
        self.data = "" #데이터 삭제name

        return mapCodes #맵코드 목록 반환
    
    def readyPlayer(self): #단순 준비 활성화 함수
        self.tcpSock.send("1006".encode())

    def unReady(self): #준비 비활성화 함수
        self.tcpSock.send("1007".encode())

    def ready2Start(self):
        print("r2s")
        global roominfo
        playerReadyDict = strToDict(roominfo[3])
        if False in playerReadyDict.values():
            print("NOREADY", playerReadyDict.values)
            return "NOREADY"
        else:
            print("1008 전송")
            self.tcpSock.send("1008".encode())
            return "Ready"


    def setGame(self, mapCode):
        global roominfo
        '''
        recv의 병목현상 때문에, 스레드로 실행한다.
        이곳에선 맵의 존재 udp통신 실행 등등 게임 시작 전의 모든 과정을 처리한다.
        
        
        '''
        self.startGame = False #게임 시작 트리거 초기화, 서버로 부터 모든 플레이어가 준비가 끝남을 받았을때 작동됨
        
        
        print("정보 받기 시작")

        print(mapCode)

        if f"{mapCode}.dat" in os.listdir("./maps/extensionMap"): #서버다운 맵들 중 맵이 존재하는지 확인했을 때 존재하면
            print("ALREADYMAP보냄")
            self.tcpSock.send("ALREADYMAP".encode())
            #맵 존재한다고 시그널 보내기, udp연결 하기 
            
            
            #udp연결하는 함수 실행
            print("여기부터udp")
            
            self.wating = True
            time.sleep(1) #체킹 시작 기다리기

            screen.fill(T1_BG)
            btn = Button(T1_BG, "다른 플레이어를 기다리는 중...", T1_TEXT, 1, SCRSIZEX // 4, SCRSIZEY // 4, SCRSIZEX // 2, SCRSIZEY // 2)
            btn.displayButton()
            pygame.display.update()

            while not self.startGame: #모든 플레이어가 준비되, 게임 시작하라는 메세지가 올때 까지
                pass
            #udp 통신 시작하는 코드

            print("while문 나감")

            tempRoomInfo = roominfo

            while tempRoomInfo == "False" or tempRoomInfo == False:
                tempRoomInfo = roominfo
            print(tempRoomInfo)

            roomName = tempRoomInfo[0]
            mapCode = tempRoomInfo[2]
            self.playerList = strToList(roominfo[1])
            print(self.playerList)

            

            #아래에 이거 하기전에, 맵 정보 한번 더 불러오는게 권장돔
            main.multiGamePlay(self.playerList, roomName, self.nickName, mapCode) #main내의, 인스턴스 생성 신호
            self.udpPlay = main.udpHandler #인스턴스 연결

            self.udpPlay.runGame = ""
            self.isudp = True

            print("인스턴스 생성 완료")

            
            self.udpPlay.standingBy() #준비 시작
            print("main.py실행함")
            

            return                




        else: #존재 안 하면, 맵 다운 받아야 함
            
            
            print(mapCode)

            res = self._downloadMap(mapCode=mapCode) #맵 다운로드 하기

            if res == "OK":
                #대기,

                print("대기중")
                print("기다리기 메세지 전송")

                self.wating = True #방화면 불러오는거 멈추기
                time.sleep(1) #체킹 시작 기다리기

                screen.fill(T1_BG)
                btn = Button(T1_BG, "다른 플레이어를 기다리는 중...", T1_TEXT, 1, SCRSIZEX // 4, SCRSIZEY // 4, SCRSIZEX // 2, SCRSIZEY // 2)
                btn.displayButton()
                pygame.display.update()

                while not self.startGame: #모든 플레이어가 준비되, 게임 시작하라는 메세지가 올때 까지
                    pass
                #udp 통신 시작하는 코드

                print("while문 나감")

                tempRoomInfo = roominfo
                if tempRoomInfo == "False":
                    print("방정보 가져오기 실패하뮤 ㅜㅜ")


                roomName = tempRoomInfo[0]
                mapCode = tempRoomInfo[2]
                self.playerList = strToList(roominfo[1])
                print(self.playerList)

                

                #아래에 이거 하기전에, 맵 정보 한번 더 불러오는게 권장돔
                main.multiGamePlay(self.playerList, roomName, self.nickName, mapCode) #main내의, 인스턴스 생성 신호
                self.udpPlay = main.udpHandler #인스턴스 연결
                self.udpPlay.runGame = ""
                self.isudp = True
                print("인스턴스 생성 완료")
                
                self.udpPlay.standingBy() #준비 시작
                print("main.py실행함")
                

                return                



            elif res.startswith("FAIL"):
                #실패시,
                global joinedRoomName
                joinedRoomName = "" #방에서 나가기(강제)
                return


            #print(res)
            
            # if res == "FAIL": #실패하면
            #     self.tcpSock.send("0000".encode()) #클라이언트 실패 시그널 전송
            #     global joinedRoomName
            #     joinedRoomName = "" #방나가기
            #     return "FAIL" #시작 실패보내기 >> 방에서 나가져야 함
            
            # elif res == "OK":
            #     self.tcpSock.send("0080".encode()) #클라이언트 성공 시그널 전송
            # else:
            #     self.tcpSock.send("0000".encode()) #그래도 일단 실패 시그널
            #     pass #이러는 경우는 없다 사실상

            
            # self.cmd = ""
            # while self.cmd == "": #기다리기
            #     pass
            
            # print(self.cmd, "CMD")
            


            # if self.cmd == "smterr": #서버측에서 무언가 오류가 난 경우
            #     joinedRoomName = "" #방 나가기
            #     self.cmd = ""
            #     return "SERVERFAIL" #서버 실패 보내기 >> 방ㅇ서 나가져야 함

            return
                    
                
                

                

    
    



    def _downloadMap(self, mapCode):
        '''
        맵을 다운로드 받는 내부 함수, ready2Start함수에서만 실행됨
        성공 > OK, 실패 > FAIL


        한번에 여러번 보내면, 데이터가 중첩되어 사라질 수 있어서, 데이터를 수신시 그 다음 송신 요청하는 코드를 보내야 한다.
        '''
        print("READY2GET보냄")

        self.tcpSock.send("READY2GET".encode()) #다운 필요 신호, 맵 다운 시작 신호 >> 여기서부터 오는 메세지는 맵 파일이다

        self.wating = True
        time.sleep(1) #화면 멈추기

        screen.fill(T1_BG)
        btn = Button(T1_BG, "맵 다운로드 중...", T1_TEXT, 1, SCRSIZEX // 4, SCRSIZEY // 4, SCRSIZEX // 2, SCRSIZEY // 2)
        btn.displayButton()
        pygame.display.update()



        with open(f"./maps/extensionMap/{mapCode}.dat", "w") as f: #파일 읽어서 저장 시작
            print("파일 쓰기")
            try:
                while True: #EOF명령(*)을 받으면, 쓰기 종료
                    while self.mapStream == "":
                        pass #공백이면, 대기


                    

                    
                    logger.debug(f"stream을 읽어와, 쓴다 {self.mapStream}")
                    f.write(self.mapStream[1:]) #stream 쓰기 (앞문자인 ^을 빼고)
                    
                    if self.mapStream.strip()[-1] == "*": #마지막 문자가 *이면 (종료면)
                        self.tcpSock.send("mapOk".encode())
                        logger.debug("마지막, mapOk전송")
                        self.mapStream = "" #초기화
                        break #종료
                    else:
                        self.mapStream = "" #다시 받기전, 원래 버퍼를 초기화
                        self.tcpSock.send("mapOk".encode())
                        logger.debug("스탠디 바이, mapOk전송")
                        



                print("완료")
                f.close() #파일 저장

                print("성공")

                self.wating = False
                return "OK"
            
            except Exception as e:
                print("맵읽기버그!")
                self.wating = False
                return f"FAIL, {e}"

            '''
                #대충 udp연결 시작하는 내용
                print("여기부터udp")


                tempRoomInfo = self.getRoomInfo()
                if tempRoomInfo == "False":
                    print("방정보 가져오기 실패하뮤 ㅜㅜ")


                roomName = tempRoomInfo[0]
                mapCode = tempRoomInfo[2]
                print("서버 데이터받음")

                

                #아래에 이거 하기전에, 맵 정보 한번 더 불러오는게 권장돔
                main.multiGamePlay(self.players, roomName, self.nickName, mapCode) #main내의, 인스턴스 생성 신호
                self.udpPlay = main.udpHandler #인스턴스 연결
                
                self.udpPlay.standing By() #준비 시작

                return "OK"
                
            '''

            

  
    
    def quitGame(self): #게임에서 자기가 나갈때, main에서 실행된다.     그리고, 응답 받으면 recv핸들러에서 처리
        self.tcpSock.send(f"QUITGAME!{self.nickName}".encode())



class Image: #화면에 표시할 기능없는 이미지
    def __init__(self, imageName:str, posX :int, posY:int, width:int, height:int):    

        self.image = pygame.transform.scale(pygame.image.load(f"./images/lobby/{imageName}.png"), (width, height))

        self.posX = posX
        self.posY = posY
        return
    def displayImage(self):
        screen.blit(self.image, (self.posX, self.posY))

class Button: #로비에서 클릭이벤트가 있을때 검사할 버튼 객체
    def __init__(self, backColor, text : str, textColor, fontTextType ,posX :int, posY:int, width:int, height:int, function = None, parameter1 = None, parameter2 = None, parameter3 = None): 
        # backColor: 버튼의 색상
        # text, textColor: 버튼에 표시될 문자열, 그 색상
        # fontTextType = (폰트경로, 0:영어/1:한글) or 0:영어/1:한글;자동폰트설정
        # 
        # posX,posY: 버튼의 왼쪽위 꼭짓점 좌표
        # width, height: 버튼 크기
        # function: 작동할 함수

        self.backColor = backColor
        self.text = text
        self.textColor = textColor
        self.posX = posX
        self.posY = posY
        self.width = width 
        if type(fontTextType) == int: #한글/영어 유무만 주어졌다면
            self.font = "fonts/Ramche.ttf"
            self.textType = fontTextType
        else:
            self.font = fontTextType[0]
            self.textType = fontTextType[1]
        self.height = height
        self.function = function
        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.parameter3 = parameter3
        return

    def checkMouse(self): # 마우스가 버튼 위에 있는지 여부 반환

        mousePos = pygame.mouse.get_pos() # 마우스 좌표

        if self.posX + self.width > mousePos[0] > self.posX and self.posY + self.height > mousePos[1] > self.posY and self.function != None: #마우스의 위치가 버튼 안쪽이라면
            return True
        else:
            return False
    
    def displayButton(self): #버튼 표시
        
        if self.backColor != None: #배경색이 None이 아니라면(존재한다면)
            if self.checkMouse() and self.function != None: #마우스의 위치가 버튼 안쪽이라면
                pygame.draw.rect(screen, darkColor(self.backColor), [self.posX, self.posY, self.width, self.height]) #좀더 어둡게 버튼 색상 변경
            else:
                pygame.draw.rect(screen, self.backColor, [self.posX, self.posY, self.width, self.height]) #기본 버튼 색상
            
        
        if self.textColor != None and len(self.text) > 0: #텍스트 색이 None이 아니라면
            if self.textType == 0: #영어일시
                font = pygame.font.Font(self.font, 200) #폰트 설정\
                textlen = len(self.text)
            elif self.textType == 1: #한글일시
                font = pygame.font.Font(self.font, 200)
                textlen = len(self.text) * 2 #글자 가로 크기를 2배
            
            

            img = font.render(self.text, True, self.textColor) #렌더
            
            if self.width > self.height * textlen // 2: #가로가 세로의 두배 이상일시
                marginy = 0.8
                img = pygame.transform.scale(img, (self.height * textlen // 2  * marginy, self.height *marginy)) #세로기준
                screen.blit(img, (self.posX+self.width//2-self.height * textlen  * marginy // 4,self.posY + self.height//2 - self.height * marginy // 2)) #텍스트 표시
            else: #아닐시
                img = pygame.transform.scale(img, (self.width, self.width // textlen * 2)) #가로기준
                screen.blit(img, (self.posX,self.posY+self.height//2-self.width // textlen )) #텍스트 표시
    
    def checkFunction(self): #함수 실행
        if self.checkMouse() and self.function != None:
            if self.parameter3 != None:
                self.function(self.parameter1, self.parameter2,self.parameter3)
            elif self.parameter2 != None:
                self.function(self.parameter1, self.parameter2)
            elif self.parameter1 != None:
                self.function(self.parameter1)
            else:
                self.function()
            return True
        else:
            return False


currentImageList = []# 현재 사용중인 이미지의 리스트
currentButtonList = [] # 현재 사용중인 버튼의 리스트

global refreshRoomList #룸 새로고침 여부

pygame.init() # initialize pygame

clock = pygame.time.Clock() #FPS 설정

done = False #pygame 종료용 트리거

user32 = ctypes.windll.user32

SCRSIZEX = user32.GetSystemMetrics(0) #화면의 해상도 (픽셀수) 구하기 가로
SCRSIZEY = user32.GetSystemMetrics(1) #" 세로

size = (int(SCRSIZEX), int(SCRSIZEY)) # set screen size
screen = pygame.display.set_mode(size)
pygame.display.set_caption("RGB")

WHITE = [255, 255, 255]
GRAY = [127, 127, 127]
BLACK = [0,0,0]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
LIGHTBLUE = [200, 200, 255]

#THEME1
T1_BG = [24, 61, 61]
T1_BTNBG = [4, 13, 18]
T1_TEXT = [147, 177, 166]
T1_OBJ = [92, 131, 116]



def quit(): #종료함수
    global done
    done = True
    return

def lobbyButtons(): #처음 시작 장면 
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = quit

    currentButtonList.append(Button( T1_BTNBG,"싱글플레이", T1_TEXT, 1, SCRSIZEX // 3, SCRSIZEY // 2, SCRSIZEX // 3, SCRSIZEY * 3 // 40, singleButtons))
    currentButtonList.append(Button( T1_BTNBG,"멀티플레이", T1_TEXT, 1, SCRSIZEX // 3, SCRSIZEY * 5 // 8 , SCRSIZEX // 3, SCRSIZEY * 3 // 40, multiButtons))
    currentButtonList.append(Button( T1_BTNBG,"설정", T1_TEXT, 1, SCRSIZEX // 3, SCRSIZEY *3 // 4, SCRSIZEX // 3, SCRSIZEY * 3 // 40, test))
    currentButtonList.append(Button( T1_BTNBG,"종료", T1_TEXT, 1, SCRSIZEX // 3, SCRSIZEY * 7 // 8, SCRSIZEX // 3, SCRSIZEY * 3 // 40, quit))
    return

def singleButtons(): #싱글플레이
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = lobbyButtons


    currentImageList.append(Image("story", SCRSIZEX // 5 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))
    currentImageList.append(Image("custom", SCRSIZEX * 11 // 20 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))
    currentButtonList.append(Button( T1_BTNBG,"", None, 1, SCRSIZEX // 5 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2, storyButtons))
    currentButtonList.append(Button( T1_BTNBG,"", None, 1,SCRSIZEX * 11 // 20 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2, customButtons))
 

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_BTNBG, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    currentButtonList.append(Button( T1_BTNBG,"스토리", T1_TEXT, 1, SCRSIZEX // 5, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, storyButtons))
    currentButtonList.append(Button( T1_BTNBG,"커스텀", T1_TEXT, 1,SCRSIZEX * 11 // 20, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, customButtons))
    return

def customButtons(): #커스텀 선택창
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = singleButtons


    currentImageList.append(Image("Editor", SCRSIZEX // 5 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))
    currentImageList.append(Image("Play", SCRSIZEX * 11 // 20 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))
    currentButtonList.append(Button( T1_BTNBG,"", None, 1, SCRSIZEX // 5 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2, runEditor))
    currentButtonList.append(Button( T1_BTNBG,"", None, 1,SCRSIZEX * 11 // 20 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2, PlayButtons))
 

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", T1_BTNBG, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    currentButtonList.append(Button( T1_BTNBG,"맵 에디터", T1_TEXT, 1, SCRSIZEX // 5, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, runEditor))
    currentButtonList.append(Button( T1_BTNBG,"플레이", T1_TEXT, 1,SCRSIZEX * 11 // 20, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, PlayButtons))
    return

def PlayButtons(page:int = 1):

    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = customButtons

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_BTNBG, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    filelist = os.listdir("./maps/")
    print(filelist)
    mapCodeList = []
    for fileName in filelist:
        if ".dat" in fileName:
            mapCodeList.append(fileName[:-4])  #.dat을 뺀 맵 이름만 저장

    

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_TEXT, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, chooseMap, "*NONE*")) #undo 버튼
    
    currentImageList.append(Image( "refresh", SCRSIZEX - SCRSIZEX//20, 0 // 20, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_TEXT, 0, SCRSIZEX - SCRSIZEX//20, 0, SCRSIZEX // 20, SCRSIZEY // 20, PlayButtons, 1)) #새로고침 버튼

    mapCount = len(mapCodeList)

    pageCount = (mapCount - 1) // 5 + 1

    if mapCount == 0: #맵이 없네
        pass

    else: #맵이 있다
        currentPageMaps = mapCodeList[page * 5 - 5:page * 5] #현재 페이지의 맵 목록 불러오기

        for i in range(len(currentPageMaps)): #현재 페이지의 맵 수만큼
            mapCode = currentPageMaps[i].replace(".dat","")
            currentButtonList.append(Button( T1_BTNBG,mapCode, T1_TEXT, 0, SCRSIZEX // 10, SCRSIZEY // 6 + i * SCRSIZEY // 6, len(mapCode) * (SCRSIZEY // 8) // 2, SCRSIZEY // 8, openCustomMap, mapCode))
        pass
    
        if page != 1: #1페이지가 아니라면
                #왼쪽으로 버튼 추가
                currentButtonList.append(Button( T1_BTNBG,"<", T1_TEXT, 0,0,SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, PlayButtons, page - 1))

        if page != pageCount: #끝 페이지가 아니라면
            #오른쪽으로 버튼 추가
            currentButtonList.append(Button( T1_BTNBG,">", T1_TEXT, 0, SCRSIZEX - SCRSIZEY // 14, SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, PlayButtons, page + 1))
        pass

    #안내 버튼
    currentButtonList.append(Button( T1_BTNBG,"맵을 고르세요!", T1_TEXT, 1, SCRSIZEX//5, 0, SCRSIZEX * 3 // 5, SCRSIZEY // 20))
    return

def runEditor():
    global inEditor
    inEditor = True
    editor.runEditor()
    inEditor = False

def storyButtons(): #스토리모드 = 챕터선택창
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = singleButtons

    currentButtonList.append(Button( T1_OBJ,"챕터 선택", T1_TEXT, 1, SCRSIZEX // 4, SCRSIZEY // 10 , SCRSIZEX // 2, SCRSIZEY // 10))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_TEXT, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    for i in range(3):
        currentImageList.append(Image(f"chaptericons/{i+1}", SCRSIZEX * (i * 4 + 1) // 13 , SCRSIZEY // 2 - SCRSIZEX * 3 // 26, SCRSIZEX * 3 // 13, SCRSIZEX * 3 // 13))
        currentButtonList.append(Button( GRAY, "", T1_BTNBG, 0, SCRSIZEX * (i * 4 + 1) // 13, SCRSIZEY // 2 - SCRSIZEX * 3 // 26, SCRSIZEX * 3 // 13, SCRSIZEX * 3 // 13, chapterButtons, i + 1))
        currentButtonList.append(Button( T1_BTNBG, f"CHAPTER{i+1}", T1_TEXT, 0, SCRSIZEX * (i * 4 + 1) // 13, SCRSIZEY // 2 + SCRSIZEX * 3 // 26, SCRSIZEX * 3 // 13, SCRSIZEX * 3 // 65, chapterButtons, i + 1))

    return

def chapterButtons(chapter:int): #챕터 내부 = 레벨선택창
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화
    
    global currentundo
    currentundo = storyButtons

    levelCount = None #총 레벨의 수

    levelCount, clearedList = getChapterInfo(chapter)

    currentButtonList.append(Button( T1_OBJ,"레벨 선택", T1_TEXT, 1, SCRSIZEX // 4, SCRSIZEY // 10 , SCRSIZEX // 2, SCRSIZEY // 10))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", T1_BTNBG, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼
    
    
    margin = SCRSIZEX // (levelCount * 4)
    boxLength = margin * 3

    for i in range(levelCount):
        if i <= (levelCount-1) // 2: #윗줄
            #currentImageList.append(Image( "stage1", margin * (i * 8 + 1), SCRSIZEY // 2 - boxLength, boxLength, boxLength))
            currentButtonList.append(Button( T1_BTNBG, f"{i+1}", T1_TEXT, 0, margin * (i * 8 + 1), SCRSIZEY // 2 - boxLength, boxLength, boxLength, openStoryMap, chapter, i+1))
            if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                currentButtonList.append(Button( None, "클리어!", T1_TEXT, 1, margin * (i * 8 + 1), SCRSIZEY // 2, boxLength, boxLength//4))
        else:
            #currentImageList.append(Image( "stage1", margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY // 2 + margin, boxLength, boxLength))
            if levelCount % 2 == 0:
                currentButtonList.append(Button( T1_BTNBG, f"{i+1}", T1_TEXT, 0, margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY - boxLength - margin, boxLength, boxLength, openStoryMap, chapter, i+1))
                if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                    currentButtonList.append(Button( None, "클리어!", T1_TEXT, 1, margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY - margin, boxLength, boxLength//4))
        
            else:
                currentButtonList.append(Button( T1_BTNBG, f"{i+1}", T1_TEXT, 0, margin * ((i - levelCount // 2 - 1) * 8 + 1), SCRSIZEY - boxLength - margin, boxLength, boxLength, openStoryMap, chapter, i+1))
                if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                    currentButtonList.append(Button( None, "클리어!", T1_TEXT, 1, margin * ((i - levelCount // 2 - 1) * 8 + 1), SCRSIZEY - margin, boxLength, boxLength//4))

def getChapterInfo(chapter: int): #현재 챕터의 info.dat 파일 해석, 내용 반환
    with open(f"./maps/story/chapter{chapter}/info.dat", "r") as f: #챕터 정보 파일 열기
        lines = f.readlines()
        for line in lines:
            if "level=" in line: #총 레벨의 수
                levelCount = int(line.strip("level="))
            if "cleared=" in line: #클리어된 레벨 목록
                temp = line.strip("cleared=")
                clearedList = list(map(lambda x: int(x),temp.split(","))) #문자열의 정수들을 리스트에 저장 
    return levelCount, clearedList

def openStoryMap(chapter: int,level: int): #[챕터번호, 레벨번호]

    while True:
        clear = main.runGame(f"maps/story/chapter{chapter}/level{level}")
        if clear == 1: #레벨 클리어시

            levelCount, clearedList = getChapterInfo(chapter)

            if level not in clearedList: #클리어 목록에 레벨이 없다면
                with open(f"./maps/story/chapter{chapter}/info.dat", "a") as f: #챕터 정보 파일 뒤에 이어서 쓰기
                    f.write(f",{level}")
            
            if level < levelCount:
                openStoryMap(chapter, level+1)

            break
        elif clear == 2: #레벨 직접 중단시
            break
    chapterButtons(chapter)
    return

def openCustomMap(mapCode:str): #커스텀 맵 열기
    while True:
        clear = main.runGame(f"maps/{mapCode}")
        if clear != 0: # 직접 중단 or 클리어시
            break
    return

def undo():

    if currentundo != None: #현재 undo로 지정된 함수 실행
        currentundo()

    return

def getString(filter, lengthLimit = 12):

    string = ""

    strDone = False    

    screen.fill(T1_BG) #배경 띄우기

    #규칙 메세지 2줄로
    nameRule1 = Button(None, "이름은 최대 12글자입니다!", T1_TEXT, 1, 0, SCRSIZEY //2 + SCRSIZEY //20, SCRSIZEX, SCRSIZEY//20)
    
    if filter == re.compile('[a-zA-Z0-9]+'): #영문 or 숫자
        nameRule2 = Button(None, "영어 대소문자 또는 숫자만 사용할 수 있습니다", T1_TEXT, 1, 0, SCRSIZEY//2 + SCRSIZEY//10 ,SCRSIZEX, SCRSIZEY//20)
    
    elif filter == re.compile('[a-zA-Z]+'): #영문일 경우
        nameRule2 = Button(None, "영어 대소문자만 사용할 수 있습니다", T1_TEXT, 1, 0, SCRSIZEY//2 + SCRSIZEY//10 ,SCRSIZEX, SCRSIZEY//20)
    
    nameRule1.displayButton() 
    nameRule2.displayButton()

    behindScreener = Button(WHITE, "None", None, 0, SCRSIZEX//4, SCRSIZEY//4, 12 * SCRSIZEX//24, SCRSIZEX//12) #이름 입력칸 뒤에 올 것(리셋을 위해)

    while not strDone: #먼저 이름을 입력 받은 후 서버와 통신한다.
        clock.tick(60)
        nameScreener = Button(None, string, BLACK, 0, SCRSIZEX//4, SCRSIZEY//4, SCRSIZEX//2, SCRSIZEX//12)

        #화면에 띄우기
        behindScreener.displayButton()
        nameScreener.displayButton() 

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 종료 이벤트
                global done
                done=True
                return

            if event.type == pygame.KEYDOWN: #키가 눌렸을 때
                if event.key == pygame.K_SPACE: #스페이스면
                    pass #무시

                elif event.key == pygame.K_RETURN: #엔터면
                    strDone = True
                
                elif event.key == pygame.K_ESCAPE: #ESC면
                    return "/ESC" #탈출

                elif event.key == pygame.K_BACKSPACE: #뒤로가기
                    string = string[:-1] #맨 오른쪽 빼고 저장
                
                else:
                    if len(string) < 12: #12글자 미만일 때만
                        if filter.match(event.unicode) != None:
                            string += event.unicode #쓰기
        

    if string == "":
        return "default"
    
    return string

def multiButtons(): #멀티플레이, 시작 전 화면
    global connected
    global tcpHandler
    print("connected:",connected)

    if connected: #연결이 되어있다면, 바로 방 목록으로 ㄱㄱ
        serverRoomList(tcpHandler, 1)
        return

    nameError = Button(None, "이름에 문제가 있습니다. 다시 설정해 주세요", T1_TEXT, 0, SCRSIZEX//4, SCRSIZEY//2 + SCRSIZEY//20 ,SCRSIZEY, SCRSIZEY//20)

    connecting = Button(None, "서버 연결 중...", T1_TEXT, 0, SCRSIZEX//2, SCRSIZEY //2, SCRSIZEY * 3 // 8, SCRSIZEY//20) #서버 연결 메세지 표시

    done = False

    pygame.display.update()#화면 업데이트

    if done:
        return
    
    
    tcpHandler = conTcp() #tcp 핸들러 시작 (반복문 벗어나면)
    nameDone = False

    while not nameDone:
        nickName = getString(re.compile('[a-zA-Z0-9]+')) #이름 변수 설정

        print("이름 입력 완료")

        if nickName == "/ESC":
            return #로비로 돌아가기
        
        print(nickName)
        
        screen.fill(T1_BG) #검은 화면

        connecting.displayButton()



        if connected:
            if tcpHandler.setName(nickName): #이름 설정 요청 보냈을 때 성공이면 True 변환
                serverRoomList(tcpHandler) #대충 매뉴화면 나오게 하는 함수
                nameDone = True

        elif tcpHandler.run(): #run했을때, 실행 완료(True)면


            connected = True
            handlerThread = threading.Thread(target=tcpHandler.recvRoom) #메시지 수신 핸들러 스레드 실행
            handlerThread.daemon = True #데몬 스레드로 설정
            handlerThread.start()
            
            if tcpHandler.setName(nickName): #이름 설정 요청 보냈을 때 성공이면 True 변환
                
                print("이름 설정 성공")
                nameDone = True
                serverRoomList(tcpHandler) #방 목록 나오는 함수
                
                return

                
            else:
                screen.fill(T1_BG) 
                nameError.displayButton() #이름 재설정 부탁해요 띄우기.   
        else:
            print("이름 설정 실패")
            return    
        
        

        pygame.display.update()

    
                

def serverRoomList(handler: classmethod, page:int = 1): 

    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화
    
    global currentundo
    currentundo = lobbyButtons

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_TEXT, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼
    
    currentImageList.append(Image( "refresh", SCRSIZEX - SCRSIZEX//20, 0 // 20, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_TEXT, 0, SCRSIZEX - SCRSIZEX//20, 0, SCRSIZEX // 20, SCRSIZEY // 20, serverRoomList, handler, 1)) #새로고침 버튼

    roomList = handler.checkRoomList() #방 목록을 리스트로 반환한다,

    print(roomList)

    roomCount = len(roomList)

    pageCount = (roomCount - 1) // 5 + 1

    print(roomCount)

    if roomList[0] == "*EMPTY*": #방이 없네
        pass

    else: #방이 있다
        currentPageRooms = roomList[page * 5 - 5:page * 5] #현재 페이지의 방 목록 불러오기

        for i in range(len(currentPageRooms)): #현재 페이지의 방 수만큼

            
            roomName = currentPageRooms[i].split(",")[0]
            playerCount = int(currentPageRooms[i].split(",")[1])

            showText = f"{roomName}|{playerCount}/4"

            currentButtonList.append(Button( T1_BTNBG,roomName, T1_TEXT, 0, SCRSIZEX // 10, SCRSIZEY // 6 + i * SCRSIZEY // 6, len(roomName) * (SCRSIZEY // 8) // 2, SCRSIZEY // 8, handler.joinRoom, roomName))

            
    
        if page != 1: #1페이지가 아니라면
                #왼쪽으로 버튼 추가
                currentButtonList.append(Button( T1_BTNBG,"<", T1_TEXT, 0,0,SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverRoomList, handler, page - 1))

        if page != pageCount: #끝 페이지가 아니라면
            #오른쪽으로 버튼 추가
            currentButtonList.append(Button( T1_BTNBG,">", T1_TEXT, 0, SCRSIZEX - SCRSIZEY // 14, SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverRoomList,handler, page + 1))
        pass

    #방 추가 버튼
    currentButtonList.append(Button( T1_BTNBG,"방 만들기", T1_TEXT,1, SCRSIZEX//5, 0, SCRSIZEX * 3 // 5, SCRSIZEY // 20, serverMakeRoom, handler))

def serverMakeRoom(handler: classmethod):

    roomDone = False

    while not roomDone: #계속 반복

        print("방만드는중")

        roomName = getString(re.compile('[a-zA-Z]+')) #필터 설정(영문만 가능)

        if roomName == "/ESC": #탈출
            return
        
        print("방이름 :",roomName)
        
        if handler.makeRoom(roomName): #방 만들기
            print("방 만들기 성공")
            roomDone = True

            global joinedRoomName
            joinedRoomName = roomName
            serverJoinedRoom(handler)
            return #함수 종료
        else: 
            print("방 만들기 실패")
            
def serverJoinedRoom(handler: classmethod):

    global joinedRoomName
    global choosedMultiMap
    global clock
    global currentMapCode
    global roominfo
    fixedButtonList, fixedImageList = [], []

    print(joinedRoomName, "들어옴")


    roomTitleButton1 = Button( T1_BTNBG,"방:", T1_TEXT, 0, 0, SCRSIZEY // 10, SCRSIZEX // 20, SCRSIZEY // 10) #방 제목
    roomTitleButton2 = Button( T1_BTNBG,joinedRoomName, T1_TEXT, 0, SCRSIZEX // 20, SCRSIZEY // 10, len(joinedRoomName) * SCRSIZEX // 40, SCRSIZEY // 10) #방 제목
    setMapCodeButton = Button( T1_BTNBG,"맵 바꾸기", T1_TEXT, 1, SCRSIZEX//5, 0, SCRSIZEX * 3 // 5, SCRSIZEY // 20, serverBrowseMap, handler, handler.getMapCodeList())


    fixedButtonList = [] #변하지 않는 버튼 리스트 ex) 방 제목, 나가기
    fixedButtonList.append(roomTitleButton1)
    fixedButtonList.append(roomTitleButton2)
    fixedButtonList.append(setMapCodeButton)
    fixedImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20)) #undo 버튼
    fixedButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, handler.leaveRoom)) #undo 버튼

    roominfo = False
    print("스레드 시작함")
    banginfoThread = threading.Thread(target=handler.getRoomInfo)
    banginfoThread.daemon = True
    banginfoThread.start()
    
    print("스레드 성공")
    while roominfo == False: #기다리기
        pass
    while joinedRoomName != "":
        if handler.isudp:
            if handler.udpPlay.runGame != "":
                print("오!!", handler.udpPlay.runGame,handler.udpPlay.otherPlayer )
                clear = 0
                while clear == 0:
                    clear = main.runGame(handler.udpPlay.runGame, "MultiPlay", handler.udpPlay.otherPlayer)
                
                handler.isudp = False
                handler.udpPlay.done = True
                handler.udpPlay.runGame = ""
                handler.quitGame()
                
                print("게임 종료")

        if tcpHandler.wating and handler.isudp == False:
            screen.fill(GREEN)
            pygame.display.update()
            print("quitGame상태")

        if not tcpHandler.wating: #맵 다운이거나, 다른플레이 기다릴때 이게 작동됨
            clock.tick(60)

            if roominfo != False:
                joinedRoomName = roominfo[0]
                playerList = strToList(roominfo[1])

                currentMapCode = roominfo[2]
                playerReadyDict = strToDict(roominfo[3])
                isGameReady = strToBool(roominfo[4])
            screen.fill(T1_BG)

            if choosedMultiMap != False: #맵을 골랐을 시!!
                if choosedMultiMap == "*NONE*":
                    choosedMultiMap = False #무효일시 넘어가기
                else: #유효할 시
                    handler.setMap(choosedMultiMap) #맵 설정 요청
                    choosedMultiMap = False #맵을 다시 고를 수 있다는 뜻

            

            ReadyButton = None
            startButton = None
            
            playerButtonList = []

            for i, player in enumerate(playerList):
                showingText = f"{i+1}. {player} " +("Ready" if playerReadyDict[player] else "") #플레이어 이름과 준비상태로 텍스트 만들기
                playerButtonList.append(Button( T1_BTNBG, f"/ {showingText}", T1_OBJ, 0, 0, SCRSIZEY // 5 + SCRSIZEY // 10 * (i+1), SCRSIZEY // 40 * len(showingText), SCRSIZEY // 20))

            if currentMapCode == "": #현재 맵코드가 없을시
                mapCodeText = "mapcode:*EMPTY*" #맵이 없음
            else: #맵코드가 있을시
                mapCodeText = f"mapcode:{currentMapCode}"
                if playerReadyDict[handler.nickName] == True: #준비상태라면
                    ReadyButton = Button( T1_BTNBG, "준비 해제", T1_TEXT, 1, SCRSIZEX * 3 // 8, SCRSIZEY // 20 + SCRSIZEX // 30, SCRSIZEX // 4, SCRSIZEX // 36, handler.unReady)
                    if handler.nickName == playerList[0] and False not in playerReadyDict.values(): #0번 플레이어(방장)이고 모두 준비되어 있다면
                        startButton = Button( T1_BTNBG, "게임 시작!", T1_TEXT, 1, SCRSIZEX * 3 // 8, SCRSIZEY // 20 + SCRSIZEX // 15, SCRSIZEX // 4, SCRSIZEX // 36, handler.ready2Start)
                        startButton.displayButton()
                else: #준비가 아니라면
                    ReadyButton = Button( T1_BTNBG, "준비 시작", T1_TEXT, 1, SCRSIZEX * 3 // 8, SCRSIZEY // 20 + SCRSIZEX // 30, SCRSIZEX // 4, SCRSIZEX // 36, handler.readyPlayer)
                
                ReadyButton.displayButton()



                

                
                


            mapCodeButton = Button( None, mapCodeText, WHITE, 0, SCRSIZEX // 2 - (SCRSIZEX * len(mapCodeText) // 50) // 2, SCRSIZEY // 20, SCRSIZEX * len(mapCodeText) // 50, SCRSIZEX // 30)

            for button in fixedButtonList: #버튼들 모두 출력
                button.displayButton()

            for button in playerButtonList: #플레이어 이름 모두 출력
                button.displayButton()

            for button in fixedImageList: #이미지들 모두 출력
                button.displayImage()

            mapCodeButton.displayButton()

        
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # 종료 이벤트
                    global done
                    done=True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1: #좌클릭이라면   
                        for button in fixedButtonList: #마우스와 겹치는 버튼을 작동시킨다
                            if button.checkFunction():
                                break
                        if ReadyButton != None:
                            ReadyButton.checkFunction()
                        if startButton != None:
                            startButton.checkFunction()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: #ESC 누를시 방 나가기 기능
                        handler.leaveRoom()

    roominfo = ""
    print("joinedroom탈출!")
        
    return

def chooseMap(mapCode): #전역변수 choosedMultiMap를 변화시키는 함수
    global choosedMultiMap
    choosedMultiMap = mapCode
    return

def serverBrowseMap(handler ,mapCodeList:list, page:int = 1): #맵을 서버에서 검색하는 함수
    
    print(mapCodeList)
    currentImageList, currentButtonList = [],[] #초기화

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, chooseMap, "*NONE*")) #undo 버튼
    
    currentImageList.append(Image( "refresh", SCRSIZEX - SCRSIZEX//20, 0 // 20, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( T1_BTNBG,"", T1_TEXT, 0, SCRSIZEX - SCRSIZEX//20, 0, SCRSIZEX // 20, SCRSIZEY // 20, serverBrowseMap, handler, mapCodeList,1)) #새로고침 버튼

    mapCount = len(mapCodeList)

    pageCount = (mapCount - 1) // 5 + 1

    if mapCount == 0: #맵이 없네
        pass

    else: #맵이 있다
        currentPageMaps = mapCodeList[page * 5 - 5:page * 5] #현재 페이지의 맵 목록 불러오기

        for i in range(len(currentPageMaps)): #현재 페이지의 맵 수만큼
            mapCode = currentPageMaps[i].replace(".dat","")
            currentButtonList.append(Button( T1_BTNBG,mapCode, T1_TEXT, 0, SCRSIZEX // 10, SCRSIZEY // 6 + i * SCRSIZEY // 6, len(mapCode) * (SCRSIZEY // 8) // 2, SCRSIZEY // 8, chooseMap, mapCode))
        pass
    
        if page != 1: #1페이지가 아니라면
                #왼쪽으로 버튼 추가
                currentButtonList.append(Button( T1_BTNBG,"<", T1_TEXT, 0,0,SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverBrowseMap, handler, mapCodeList,page - 1))

        if page != pageCount: #끝 페이지가 아니라면
            #오른쪽으로 버튼 추가
            currentButtonList.append(Button( T1_BTNBG,">", T1_TEXT, 0, SCRSIZEX - SCRSIZEY // 14, SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverBrowseMap,handler, mapCodeList,page + 1))
        pass

    #안내 버튼
    currentButtonList.append(Button( T1_OBJ,"맵을 고르세요!", T1_TEXT, 1, SCRSIZEX//5, 0, SCRSIZEX * 3 // 5, SCRSIZEY // 20))

    screen.fill(T1_BG) #임시 배경색 (차후에 이미지로 변경될수 있음)

    for button in currentButtonList: #버튼들 모두 출력
        button.displayButton()

    for button in currentImageList: #이미지들 모두 출력
        button.displayImage()
        
    pygame.display.update() #디스플레이 업데이트

    global choosedMultiMap
    while choosedMultiMap == False: #반복문, 맵을 고를 시 함수 종료

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 종료 이벤트
                global done
                done=True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: #좌클릭이라면   
                    for button in currentButtonList: #마우스와 겹치는 버튼을 작동시킨다
                        if button.checkFunction():
                            break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #ESC 누를시
                    choosedMultiMap = "*NONE*" # 고르지 않았다는 뜻
    
    return choosedMultiMap #맵을 골랐다는 뜻

def strToDict(string:str):
    string = string.replace(" ", "") #공백 제거
    string = string.replace("{", "")
    string = string.replace("}", "") #중괄호 제거
    string = string.replace("'", "")
    string = string.replace('"', "") #따옴표 제거
    strDict = {}

    for keyValue in string.split(","):
        keyValueList = keyValue.split(":")
        

        strDict[keyValueList[0]] = strToBool(keyValueList[1])
    
    return strDict

def strToBool(string:str):
    if string == "True":
        return True
    elif string == "False":
        return False
    else:
        return string


def strToList(string:str):
    string = string.replace(" ", "") #공백 제거
    string = string.replace("[", "")
    string = string.replace("]", "") #대괄호 제거
    string = string.replace("'", "")
    string = string.replace('"', "") #따옴표 제거
    return string.split(",")








    
def test():

    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = lobbyButtons

    themeList = os.listdir('./Themes/') #현재 테마 가져오기
    themeList = map(lambda x : x.replace(".theme", ""), themeList) #뒤에 확장자 표기 제거


    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", T1_BTNBG, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    currentButtonList.append(Button( T1_BTNBG,"테마 설정", WHITE, 1, SCRSIZEX * 3 // 8, SCRSIZEY * 1 // 8, SCRSIZEX // 4, SCRSIZEY // 8))

    tempCnt = 5.5
    for t in themeList:
        t = "%-9s" % t #최대길이인 8글자에 맞춰서 공백

        currentButtonList.append(Button( T1_BTNBG, t, WHITE, 1, SCRSIZEX * 3 // 10, SCRSIZEY * tempCnt // 14, SCRSIZEX // 4, SCRSIZEY // 14, setTheme, t))
        tempCnt += 1.5
    
    return


def setTheme(theme):
    global T1_BG
    global T1_BTNBG
    global T1_TEXT
    global T1_OBJ


    theme = theme.strip()

    with open(f"./Themes/{theme}.theme", "r") as f:
        lines = f.readlines()

        print

        T1_BG = list(map(lambda x : int(x), strToList(lines[0].replace("\n", ""))))
        T1_BTNBG = list(map(lambda x : int(x), strToList(lines[1].replace("\n", ""))))
        T1_TEXT = list(map(lambda x : int(x), strToList(lines[2].replace("\n", ""))))
        T1_OBJ = list(map(lambda x : int(x), strToList(lines[3])))
        

    return







#------------------------여기부터 시작---------------------------------#

lobbyButtons()

    


while not done: # loop the game       

    clock.tick(60) #FPS는 60으로

    if inEditor: #에디터 실행중일시
        pass

    screen.fill(T1_BG) #임시 배경색 (차후에 이미지로 변경될수 있음)
    
    for button in currentButtonList: #버튼들 모두 출력
        button.displayButton()

    for button in currentImageList: #이미지들 모두 출력
        button.displayImage()

    pygame.display.update()

    if joinedRoomName != "": #방 입장시

        serverJoinedRoom(tcpHandler)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: # 종료 이벤트
            done=True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: #좌클릭이라면   
                for button in currentButtonList: #마우스와 겹치는 버튼을 작동시킨다
                    if button.checkFunction():
                        break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: #ESC 누를시 undo 기능
                undo()


            

pygame.quit() # quit pygame