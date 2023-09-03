import main
import pygame
import editor
import ctypes
import re


#요 아래는 서버용
import os
import socket
import threading
import selectors

with open("../server/serverip.txt","r") as f:
    HOST = f.readline()
PORT = 8080

inEditor = False # 에디터를 하고있는지

connected = False #서버 연결 여부

joinedRoomName = None #현재 접속중인 방의 이름

choosedMultiMap = False #멀티에서 맵을 고를 시 True로 바뀜, 다시 방 화면으로 ㄱㄱ

sel = selectors.DefaultSelector() #셀렉터 초기화


def darkColor(color): #색을 더 어둡게 
    return list(map(lambda x: x / 2, color)) #RGB 값을 모두 절반으로

class conTcp():
    def __init__(self):
        self.players = []
        self.data = None
        self.mapDownloading = False #맵 다운중에는 recv스레드 꺼놔야 해서


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

        while self.data == None:
            pass #기다리기


        print("이름 설정 중")
        if(self.data == "0080"):
            self.data = None 
            self.nickName = nickName
            return True #성공 메세지 받을 시
        else:
            self.data = None 
            return False
    
    def checkRoomList(self):
        self.tcpSock.send("0002".encode()) #룸 리스트 받기 형식 > ROOMLIST방이름!방이름!
        while self.data == None:
            pass #기다리기

        if self.data == "NULL":
            self.data = None 
            return ["*EMPTY*"]
        else:
            temp = self.data
            self.data = None 
            return temp.split("!")


    def makeRoom(self, roomCode: str): #방 만들기 (서버 상에서 자동으로 방 참여가 된다.) 이름 규칙 : 12자 내외 영문만
        self.tcpSock.send(f"0003{roomCode}".encode()) #방 생성 요청


        while self.data == None:
            pass #기다리기
        if(self.data == "0080"):
            self.data = None 
            return True #성공 메세지 받을 시 >> 클라이언트 측 핸들러에서, 룸 용 함수 실행 필요
        
        else:
            self.data = None 
            return False
            
        
    def joinRoom(self, roomCode: str): #방 참여요청

        print(roomCode)
        self.tcpSock.send(f"0004{roomCode}".encode()) #방 입장 요청

        while self.data == None:
            pass #기다리기:

        
        
        if(self.data == "0080"):
            global joinedRoomName
            joinedRoomName = roomCode
            print(roomCode, self.data)

            self.data = None
            return True #성공 메세지 받을 시
        
        
        else:
            self.data = None
            return False
    
    def setMap(self, mapCode):
        self.tcpSock.send(f"1001!{mapCode}".encode()) #맵 설정 요청

        while self.data == None:
            pass #기다리기
        
        if(self.data == "0080"):
            print(f"맵코드설정:{mapCode}")
            self.data = None 
            return True #성공 메세지 받을 시
        else:
            print("맵코드 실패?")
            self.data = None
            return False

    def leaveRoom(self):

        self.tcpSock.send("1003".encode()) #방 나가기 요청
        
        while self.data == None:
            pass #기다리기

        if(self.data == "0080"):
            print("나가기 완료")
            global joinedRoomName
            joinedRoomName = None
            self.data = None
            serverRoomList(self, 1) #방 목록 다시 불러오기
            return True #성공 메세지 받을 시
        else:
            print("나가기 실패")
            self.data = None
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
        self.data = None
        self.cmd = None
        while True:

            if not self.mapDownloading: #맵 다운이 아닐때만, 서버 메세지 받기
                recvMsg = self.tcpSock.recv(1024).decode()

                if recvMsg == "7777": #서버가 보낸 heartBeat신호일 시
                    self.tcpSock.send("7780".encode()) #응답하기

                elif recvMsg.startswith("CMD"): #CMD로 시작되는, 서버 설정 메세지인 경우
                    self.cmd = recvMsg.replace("CMD ", "")

                


                else:
                    self.data = recvMsg
                    if type(self.data) == str:
                        if not self.data.startswith("ROOMINFO"):
                            print(self.data)
            
            else:
                self.data = None #서버가 맵 정보를 받는 중이기 때문에 거의 모든 작업 보류
        
            





        #서버 메세지 필터링
        

    
    
    def getRoomInfo(self):
        
        self.tcpSock.send("1005".encode()) #방 정보 요청
        
        while self.cmd == None: #데이터 도착까지 기다리기
            pass
        
        if self.cmd.startswith("ROOMINFO"): #ROOMINFO로 시작하는 방 정보 메세지 일때
            roomIf = self.cmd.replace("ROOMINFO", "")
            roomIfList = roomIf.split("!")
            self.cmd = None
            return roomIfList
            

            #형식 ROOMINFO방이름!플레이어목록(@로 구분)!맵 코드(없으면 None)!플레이어 준비 현황({플레이어 : True or False}을 문자열로 )!True or False

                #del data #변수 참조 삭제,  받는 변수로 바뀌어서 삭제하면 안된다.
                
                #return True #성공 메세지 받을 시 <<어짜피 실행 안될텐데
            
        else: #무효일시
            #del data
            self.cmd = None
            return False
        
    def getMapCodeList(self):
        self.tcpSock.send("1000".encode()) #맵코드 목록 요청

        while self.data == None: #데이터 도착까지 기다리기
            pass
        
        mapCodes = self.data.split("!") #맵 코드로 된 리스트 생성
        self.data = None #데이터 삭제name

        return mapCodes #맵코드 목록 반환
    




    def ready2Start(self):
        self.mapDownloading = True #recv스레드 잠깐 멈추기 (맵 파일을 받을때 겹쳐서 오류)
        self.tcpSock.send("1008".encode())

        data = self.tcpSock.recv(1024)
        data = data.decode()

        while data == "" or None: #데이터 도착까지 기다리기
            pass
        
        if data == "nofile":
            print("파일 없음")
            #여기서 버튼을 수정 밍러마러ㅣㄴ멍;ㅣ

        elif data.startswith("1008"):
            mapCode = data[4:] #1008을 뺀 맵 코드를 저장

            if f"{mapCode}.dat" in os.listdir("./extensionMap"): #서버다운 맵들 중 맵이 존재하는지 확인했을 때 존재하면
                self.tcpSock.send("0000".encode())
                #맵 존재한다고 시그널 보내기, udp연결 하기 

                #udp연결하는 함수 실행


            else: #존재 안 하면, 맵 다운 받아야 함
                self.tcpSock.send("1111".encode()) #다운 필요 신호, 맵 다운 시작 신호 >> 여기서부터 오는 메세지는 맵 파일이다
                res = self._downloadMap() #맵 다운 시작

                if res == "FAIL": #실패하면
                    self.tcpSock.send("0000".encode()) #클라이언트 실패 시그널 전송
                    
                    joinedRoomName = None #방나가기
                    return "FAIL" #시작 실패보내기 >> 방에서 나가져야 함
                
                elif res == "OK":
                    self.tcpSock.send("0080".encode()) #클라이언트 실패 시그널 전송
                else:
                    pass #이러는 경우는 없다 사실상

                
                data = self.tcpSock.recv(1024) #다시데이터 받기
                while data == "" or None: #데이터 도착까지 기다리기
                    data = self.tcpSock.recv(1024) #다시데이터 다시받기

                self.mapDownloading = False #recv스레드 블락 풀기

                if data == "smterr": #서버측에서 무언가 오류가 난 경우
                    joinedRoomName = None #방 나가기
                    return "SERVERFAIL" #서버 실패 보내기 >> 방ㅇ서 나가져야 함
                
                elif data == "0080": #성공한 경우

                    return
                    #대충 udp연결 시작하는 내용

                




    def _downloadMap(self, mapCode):
        '''
        맵을 다운로드 받는 내부 함수, ready2Start함수에서만 실행됨
        성공 > OK, 실패 > FAIL
        '''

        with open(f"./extensionMap/{mapCode}.dat", "w") as f: #파일 읽어서 저장 시작
            print("파일 쓰기")
            try:
                stream = self.soc.recv(1024).decode() #먼저 1024를 읽는다.
                end = False
                while not end: #EOF명령(*)을 받으면, 쓰기 종료
                    f.write(stream) #stream 쓰기
                    print("받아오는중,,,")
                    if stream.strip()[-1] == "*": #마지막 문자가 *이면 (종료면)
                        end = True #종료
                        stream = 0
                    else:
                        stream = self.soc.recv(1024) #다시 1024만큼 읽는다. 이런 순서로 하면, 코드가 단축화 된다.

                print("완료")
                f.close() #파일 저장

                return "OK"
                

            except Exception:
                return "FAIL"



class conUdp(): #실제 게임에서 쓰는udp통신, #김동훈 작성
    def __init__(self, players: list, initPos: list, roomName: str, name: str): #players는 참여자들 닉네임 list, initPos는 플레이할 맵의 플레이어 기본위치
        self.udpSock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #기본 udp 소켓 설정
        self.roomName = roomName
        self.nickName = name
        self.playerList = {}
        for p in players:
            self.playerList[p] = initPos #플레이어 좌표 초기 설정

        self.rgb = [False, False, False]
        self.done = False

    




    def _postMan(self, msg): #메세지를 전송하는 함수
        self.udpSock.sendto(msg.encode(), (HOST, PORT))


    def udpSendHandler(self): #서버에게 커맨드를 전송하는 핸들러, 스레드 필요
        while not self.done: #게임 끝나는 신호 오기 전까지
            #res = f"P{self.roomName}!{},{}!{self.nickName}" #P방이름!좌표x,좌표y!플레이어 이름 (자신 것)
            pass
        self._postMan()





    def udpRecvHandler(self):
        while not self.done: #게임 끝나는 신호 오기 전까지
            data, addr = self.udpSock.recvfrom(1024) #1024만큼 데이터 수신
            
            data = data.decode()
            if data.startswith('P'): #위치 정보를 수신
                data = data.replace("P", "") #P삭제
                data = data.split("!") #구분자가 !라서 !를 기준으로 분리
                pos = data[1].split(",") #,기준으로 나눔 [0] : x, [1] : y
                self.playerList[data[0]] = [pos[0], pos[1]] #위치정보를 멤버 변수에 저장

            elif data.startswith('R'): #RGB변경 정보를 수신
                data = data.replace("R", "") #P삭제
                data = data.split(",")
                self.rgb[0] = data[0]
                self.rgb[1] = data[1]
                self.rgb[2] = data[2] #rgb정보 저장
        
        
    



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

    currentButtonList.append(Button( T1_OBJ,"싱글플레이", T1_BTNBG, 1, SCRSIZEX // 3, SCRSIZEY // 2, SCRSIZEX // 3, SCRSIZEY * 3 // 40, singleButtons))
    currentButtonList.append(Button( T1_OBJ,"멀티플레이", T1_BTNBG, 1, SCRSIZEX // 3, SCRSIZEY * 5 // 8 , SCRSIZEX // 3, SCRSIZEY * 3 // 40, multiButtons))
    currentButtonList.append(Button( T1_OBJ,"설정", T1_BTNBG, 1, SCRSIZEX // 3, SCRSIZEY *3 // 4, SCRSIZEX // 3, SCRSIZEY * 3 // 40, test))
    currentButtonList.append(Button( T1_OBJ,"종료", T1_BTNBG, 1, SCRSIZEX // 3, SCRSIZEY * 7 // 8, SCRSIZEX // 3, SCRSIZEY * 3 // 40, quit))
    return

def singleButtons(): #싱글플레이
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = lobbyButtons


    currentImageList.append(Image("story", SCRSIZEX // 5 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))
    currentImageList.append(Image("custom", SCRSIZEX * 11 // 20 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", T1_BTNBG, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    currentButtonList.append(Button( T1_BTNBG,"스토리", WHITE, 1, SCRSIZEX // 5, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, storyButtons))
    currentButtonList.append(Button( T1_BTNBG,"커스텀", WHITE, 1,SCRSIZEX * 11 // 20, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, runEditor))
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
    currentButtonList.append(Button( GRAY,"", T1_BTNBG, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    for i in range(5):
        currentImageList.append(Image(f"chaptericons/{i+1}", SCRSIZEX * (i * 8 + 1) // 40 , SCRSIZEY // 2 - SCRSIZEX * 3 // 40, SCRSIZEX * 3 // 20, SCRSIZEX * 3 // 20))
        currentButtonList.append(Button( GRAY, "", T1_BTNBG, 0, SCRSIZEX * (i * 8 + 1) // 40, SCRSIZEY // 2 - SCRSIZEX * 3 // 40, SCRSIZEX * 3 // 20, SCRSIZEX * 3 // 20, chapterButtons, i + 1))

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
            currentButtonList.append(Button( WHITE, f"{i+1}", BLACK, 0, margin * (i * 8 + 1), SCRSIZEY // 2 - boxLength, boxLength, boxLength, openStoryMap, chapter, i+1))
            if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                currentButtonList.append(Button( None, "클리어!", WHITE, 1, margin * (i * 8 + 1), SCRSIZEY // 2, boxLength, boxLength//4))
        else:
            #currentImageList.append(Image( "stage1", margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY // 2 + margin, boxLength, boxLength))
            if levelCount % 2 == 0:
                currentButtonList.append(Button( WHITE, f"{i+1}", BLACK, 0, margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY - boxLength - margin, boxLength, boxLength, openStoryMap, chapter, i+1))
                if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                    currentButtonList.append(Button( None, "클리어!", WHITE, 1, margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY - margin, boxLength, boxLength//4))
        
            else:
                currentButtonList.append(Button( WHITE, f"{i+1}", BLACK, 0, margin * ((i - levelCount // 2 - 1) * 8 + 1), SCRSIZEY - boxLength - margin, boxLength, boxLength, openStoryMap, chapter, i+1))
                if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                    currentButtonList.append(Button( None, "클리어!", WHITE, 1, margin * ((i - levelCount // 2 - 1) * 8 + 1), SCRSIZEY - margin, boxLength, boxLength//4))

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
    
    return clear

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
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼
    
    currentImageList.append(Image( "refresh", SCRSIZEX - SCRSIZEX//20, 0 // 20, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, SCRSIZEX - SCRSIZEX//20, 0, SCRSIZEX // 20, SCRSIZEY // 20, serverRoomList, handler, 1)) #새로고침 버튼

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

            currentButtonList.append(Button( GRAY,roomName, BLACK, 0, SCRSIZEX // 10, SCRSIZEY // 6 + i * SCRSIZEY // 6, len(roomName) * (SCRSIZEY // 8) // 2, SCRSIZEY // 8, handler.joinRoom, roomName))

            
    
        if page != 1: #1페이지가 아니라면
                #왼쪽으로 버튼 추가
                currentButtonList.append(Button( BLACK,"<", BLUE, 0,0,SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverRoomList, handler, page - 1))

        if page != pageCount: #끝 페이지가 아니라면
            #오른쪽으로 버튼 추가
            currentButtonList.append(Button( BLACK,">", BLUE, 0, SCRSIZEX - SCRSIZEY // 14, SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverRoomList,handler, page + 1))
        pass

    #방 추가 버튼
    currentButtonList.append(Button( GRAY,"방 만들기", BLACK,1, SCRSIZEX//5, 0, SCRSIZEX * 3 // 5, SCRSIZEY // 20, serverMakeRoom, handler))

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
    fixedButtonList, fixedImageList = [], []

    print(joinedRoomName, "들어옴")


    roomTitleButton1 = Button( GRAY,"방:", BLACK, 0, 0, SCRSIZEY // 10, SCRSIZEX // 20, SCRSIZEY // 10) #방 제목
    roomTitleButton2 = Button( GRAY,joinedRoomName, BLACK, 0, SCRSIZEX // 20, SCRSIZEY // 10, len(joinedRoomName) * SCRSIZEX // 40, SCRSIZEY // 10) #방 제목
    setMapCodeButton = Button( GRAY,"맵 바꾸기", BLACK, 1, SCRSIZEX//5, 0, SCRSIZEX * 3 // 5, SCRSIZEY // 20, serverBrowseMap, handler, handler.getMapCodeList())


    fixedButtonList = [] #변하지 않는 버튼 리스트 ex) 방 제목, 나가기
    fixedButtonList.append(roomTitleButton1)
    fixedButtonList.append(roomTitleButton2)
    fixedButtonList.append(setMapCodeButton)
    fixedImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20)) #undo 버튼
    fixedButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, handler.leaveRoom)) #undo 버튼

    while joinedRoomName != None:
        global clock
        clock.tick(60)

        screen.fill(T1_BG)

        if choosedMultiMap != False: #맵을 골랐을 시!!
            if choosedMultiMap == "*NONE*":
                choosedMultiMap = False #무효일시 넘어가기
            else: #유효할 시
                handler.setMap(choosedMultiMap) #맵 설정 요청
                choosedMultiMap = False #맵을 다시 고를 수 있다는 뜻

        roominfo = handler.getRoomInfo()

        joinedRoomName = roominfo[0]
        playerList = strToList(roominfo[1])
        currentMapCode = roominfo[2]
        playerReadyDict = strToDict(roominfo[3])
        isGameReady = strToBool(roominfo[4])

        ReadyButton = None
        
        playerButtonList = []

        for i, player in enumerate(playerList):
            showingText = f"{i+1}. {player} " +("Ready" if playerReadyDict[player] else "") #플레이어 이름과 준비상태로 텍스트 만들기
            playerButtonList.append(Button( WHITE, showingText, RED, 0, 0, SCRSIZEY // 5 + SCRSIZEY // 10 * (i+1), SCRSIZEY // 40 * len(showingText), SCRSIZEY // 20))

        if currentMapCode == "": #현재 맵코드가 없을시
            mapCodeText = "mapcode:*EMPTY*" #맵이 없음
        else: #맵코드가 있을시
            mapCodeText = f"mapcode:{currentMapCode}"
            if playerReadyDict[handler.nickName] == True: #준비상태라면
                ReadyButton = Button( WHITE, "준비 해제", GRAY, 1, SCRSIZEX * 3 // 8, SCRSIZEY // 20 + SCRSIZEX // 30, SCRSIZEX // 4, SCRSIZEX // 36)
            else: #준비가 아니라면
                ReadyButton = Button( WHITE, "준비 시작", GRAY, 1, SCRSIZEX * 3 // 8, SCRSIZEY // 20 + SCRSIZEX // 30, SCRSIZEX // 4, SCRSIZEX // 36)
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #ESC 누를시 방 나가기 기능
                    handler.leaveRoom()

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
    currentButtonList.append(Button( GRAY,"", BLACK, 0, SCRSIZEX - SCRSIZEX//20, 0, SCRSIZEX // 20, SCRSIZEY // 20, serverBrowseMap, handler, mapCodeList,1)) #새로고침 버튼

    mapCount = len(mapCodeList)

    pageCount = (mapCount - 1) // 5 + 1

    if mapCount == 0: #맵이 없네
        pass

    else: #맵이 있다
        currentPageMaps = mapCodeList[page * 5 - 5:page * 5] #현재 페이지의 맵 목록 불러오기

        for i in range(len(currentPageMaps)): #현재 페이지의 맵 수만큼
            mapCode = currentPageMaps[i] 
            currentButtonList.append(Button( GRAY,mapCode, BLACK, 0, SCRSIZEX // 10, SCRSIZEY // 6 + i * SCRSIZEY // 6, len(mapCode) * (SCRSIZEY // 8) // 2, SCRSIZEY // 8, chooseMap, mapCode))
        pass
    
        if page != 1: #1페이지가 아니라면
                #왼쪽으로 버튼 추가
                currentButtonList.append(Button( BLACK,"<", BLUE, 0,0,SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverBrowseMap, handler, mapCodeList,page - 1))

        if page != pageCount: #끝 페이지가 아니라면
            #오른쪽으로 버튼 추가
            currentButtonList.append(Button( BLACK,">", BLUE, 0, SCRSIZEX - SCRSIZEY // 14, SCRSIZEY // 2 - SCRSIZEY // 16 , SCRSIZEY // 14, SCRSIZEY // 8, serverBrowseMap,handler, mapCodeList,page + 1))
        pass

    #안내 버튼
    currentButtonList.append(Button( GRAY,"맵을 고르세요!", BLACK, 1, SCRSIZEX//5, 0, SCRSIZEX * 3 // 5, SCRSIZEY // 20))

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
    print("test")
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

    if joinedRoomName != None: #방 입장시

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