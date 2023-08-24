import main
import pygame
import editor
import ctypes
import re

#요 아래는 서버용
import socket
import threading

HOST = ""
PORT = 8080





def darkColor(color): #색을 더 어둡게 
    return list(map(lambda x: x / 2, color)) #RGB 값을 모두 절반으로

class Image: #화면에 표시할 기능없는 이미지
    def __init__(self, imageName:str, posX :int, posY:int, width:int, height:int):    

        self.image = pygame.transform.scale(pygame.image.load(f"./images/lobby/{imageName}.png"), (width, height))

        self.posX = posX
        self.posY = posY
        return
    def displayImage(self):
        screen.blit(self.image, (self.posX, self.posY))

class Button: #로비에서 클릭이벤트가 있을때 검사할 버튼 객체
    def __init__(self, backColor, text : str, textColor, marginx:int ,posX :int, posY:int, width:int, height:int, function = None, parameter = None): 
        # backColor: 버튼의 색상
        # text, textColor: 버튼에 표시될 문자열, 그 색상
        # marginx = text의 x방향 여백
        # posX,posY: 버튼의 왼쪽위 꼭짓점 좌표
        # width, height: 버튼 크기
        # function: 작동할 함수

        self.backColor = backColor
        self.text = text
        self.textColor = textColor
        self.posX = posX
        self.posY = posY
        self.width = width 
        self.marginx = marginx
        self.height = height
        self.function = function
        self.parameter = parameter

        return

    def checkMouse(self): # 마우스가 버튼 위에 있는지 여부 반환

        mousePos = pygame.mouse.get_pos() # 마우스 좌표

        if self.posX + self.width > mousePos[0] > self.posX and self.posY + self.height > mousePos[1] > self.posY and self.function != None: #마우스의 위치가 버튼 안쪽이라면
            return True
        else:
            return False
    
    def displayButton(self): #버튼 표시
        
        if self.backColor != None: #배경색이 None이 아니라면(존재한다면)
            if self.checkMouse(): #마우스의 위치가 버튼 안쪽이라면
                pygame.draw.rect(screen, darkColor(self.backColor), [self.posX, self.posY, self.width, self.height]) #좀더 어둡게 버튼 색상 변경
            else:
                pygame.draw.rect(screen, self.backColor, [self.posX, self.posY, self.width, self.height]) #기본 버튼 색상
            
        

        font = pygame.font.SysFont("Consolas", 200) #폰트 설정
        img = font.render(self.text, True, self.textColor) #렌더
        img = pygame.transform.scale(img, (self.width - self.marginx*2, self.height))
        screen.blit(img, (self.posX+self.marginx,self.posY)) #텍스트 표시
    
    def checkFunction(self): #함수 실행
        if self.checkMouse() and self.function != None:
            if self.parameter == None:
                self.function()
            else:
                self.function(self.parameter)
            return True
        else:
            return False

currentImageList = []# 현재 사용중인 이미지의 리스트
currentButtonList = [] # 현재 사용중인 버튼의 리스트

pygame.init() # initialize pygame

clock = pygame.time.Clock() #FPS 설정

done = False #pygame 종료용 트리거

user32 = ctypes.windll.user32

SCRSIZEX = user32.GetSystemMetrics(0) #화면의 해상도 (픽셀수) 구하기 가로
SCRSIZEY = user32.GetSystemMetrics(1) #" 세로

size = [SCRSIZEX, SCRSIZEY] # set screen size

screen = pygame.display.set_mode(size) # set pygame screen to object "screen"

WHITE = [255, 255, 255]
GRAY = [127, 127, 127]
BLACK = [0,0,0]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
LIGHTBLUE = [200, 200, 255]

def quit(): #종료함수
    global done
    done = True
    return

def lobbyButtons(): #처음 시작 장면 
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = None

    currentButtonList.append(Button( BLACK,"SINGLE PLAYER", WHITE, SCRSIZEX // 21, SCRSIZEX // 3, SCRSIZEY // 2, SCRSIZEX // 3, SCRSIZEY * 3 // 40, singleButtons))
    currentButtonList.append(Button( BLACK,"MULTI PLAYER", WHITE, SCRSIZEX // 21, SCRSIZEX // 3, SCRSIZEY * 5 // 8 , SCRSIZEX // 3, SCRSIZEY * 3 // 40, multiButtons))
    currentButtonList.append(Button( BLACK,"SETTINGS", WHITE, SCRSIZEX // 12, SCRSIZEX // 3, SCRSIZEY *3 // 4, SCRSIZEX // 3, SCRSIZEY * 3 // 40, serverRoomList, 1))
    currentButtonList.append(Button( BLACK,"QUIT", WHITE, SCRSIZEX // 9, SCRSIZEX // 3, SCRSIZEY * 7 // 8, SCRSIZEX // 3, SCRSIZEY * 3 // 40, quit))
    return

def singleButtons(): #싱글플레이
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = lobbyButtons


    currentImageList.append(Image("story", SCRSIZEX // 5 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))
    currentImageList.append(Image("custom", SCRSIZEX * 11 // 20 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    currentButtonList.append(Button( BLACK,"STORY", WHITE, SCRSIZEX // 21, SCRSIZEX // 5, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, storyButtons))
    currentButtonList.append(Button( BLACK,"CUSTOM", WHITE, SCRSIZEX // 30,SCRSIZEX * 11 // 20, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, editor.runEditor))
    return

def storyButtons(): #스토리모드 = 챕터선택창
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    global currentundo
    currentundo = singleButtons

    currentButtonList.append(Button( GRAY,"SELECT CHAPTER", BLACK, SCRSIZEX // 20, SCRSIZEX // 4, SCRSIZEY // 10 , SCRSIZEX // 2, SCRSIZEY // 10))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼

    for i in range(5):
        currentImageList.append(Image(f"chaptericons/{i+1}", SCRSIZEX * (i * 8 + 1) // 40 , SCRSIZEY // 2 - SCRSIZEX * 3 // 40, SCRSIZEX * 3 // 20, SCRSIZEX * 3 // 20))
        currentButtonList.append(Button( GRAY, "", BLACK, 0, SCRSIZEX * (i * 8 + 1) // 40, SCRSIZEY // 2 - SCRSIZEX * 3 // 40, SCRSIZEX * 3 // 20, SCRSIZEX * 3 // 20, chapterButtons, i + 1))

    return

def chapterButtons(chapter:int): #챕터 내부 = 레벨선택창
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화
    
    global currentundo
    currentundo = storyButtons

    levelCount = None #총 레벨의 수

    with open(f"./maps/story/chapter{chapter}/info.dat", "r") as f: #챕터 정보 파일 열기
        lines = f.readlines()
        for line in lines:
            if "level=" in line: #총 레벨의 수
                levelCount = int(line.strip("level="))
            if "cleared=" in line: #클리어된 레벨 목록
                temp = line.strip("cleared=")
                clearedList = list(map(lambda x: int(x),temp.split(","))) #문자열의 정수들을 리스트에 저장 


    currentButtonList.append(Button( GRAY,"SELECT LEVEL", BLACK, SCRSIZEX // 17, SCRSIZEX // 4, SCRSIZEY // 10 , SCRSIZEX // 2, SCRSIZEY // 10))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼
    
    
    margin = SCRSIZEX // (levelCount * 4)
    boxLength = margin * 3

    for i in range(levelCount):
        if i <= (levelCount-1) // 2: #윗줄
            #currentImageList.append(Image( "stage1", margin * (i * 8 + 1), SCRSIZEY // 2 - boxLength, boxLength, boxLength))
            currentButtonList.append(Button( WHITE, f"{i+1}", BLACK, margin // 2, margin * (i * 8 + 1), SCRSIZEY // 2 - boxLength, boxLength, boxLength, openStoryMap, [chapter, i+1]))
            if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                currentButtonList.append(Button( None, "CLEARED!", RED, margin // 4, margin * (i * 8 + 1), SCRSIZEY // 2, boxLength, boxLength//4))
        else:
            #currentImageList.append(Image( "stage1", margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY // 2 + margin, boxLength, boxLength))
            if levelCount % 2 == 0:
                currentButtonList.append(Button( WHITE, f"{i+1}", BLACK, margin // 2, margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY - boxLength - margin, boxLength, boxLength, openStoryMap, [chapter, i+1]))
                if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                    currentButtonList.append(Button( None, "CLEARED!", RED, margin // 4, margin * ((i - levelCount // 2) * 8 + 1), SCRSIZEY - margin, boxLength, boxLength//4))
        
            else:
                currentButtonList.append(Button( WHITE, f"{i+1}", BLACK, margin // 2, margin * ((i - levelCount // 2 - 1) * 8 + 1), SCRSIZEY - boxLength - margin, boxLength, boxLength, openStoryMap, [chapter, i+1]))
                if i+1 in clearedList: #레벨이 클리어 목록에 있으면
                    currentButtonList.append(Button( None, "CLEARED!", RED, margin // 4, margin * ((i - levelCount // 2 - 1) * 8 + 1), SCRSIZEY - margin, boxLength, boxLength//4))

def openStoryMap(chapterlevel:list): #[챕터번호, 레벨번호]

    while True:
        clear = main.runGame(f"story/chapter{chapterlevel[0]}/level{chapterlevel[1]}")
        if clear == 1: #레벨 클리어시
            
            with open(f"./maps/story/chapter{chapterlevel[0]}/info.dat", "r") as f: #챕터 정보 파일 열기
                lines = f.readlines()
                for line in lines:
                    if "cleared=" in line: #클리어된 레벨 목록
                        temp = line.strip("cleared=")
                        clearedList = list(map(lambda x: int(x),temp.split(","))) #문자열의 정수들을 리스트에 저장 
            
            if chapterlevel[1] not in clearedList: #클리어 목록에 레벨이 없다면
                with open(f"./maps/story/chapter{chapterlevel[0]}/info.dat", "a") as f: #챕터 정보 파일 뒤에 이어서 쓰기
                    f.write(f",{chapterlevel[1]}")
            break
        elif clear == 2: #레벨 직접 중단시
            break
            
    chapterButtons(chapterlevel[0]) #챕터 선택창 다시 로드하기(CLEARED! 표시를 위해)
    
    return

def undo():
    if currentundo != None: #현재 undo로 지정된 함수 실행
        currentundo()

    return

def multiButtons(): #멀티플레이, 시작 전 화면

    regularFilter = re.compile("^a-zA-Z0-9") #문자나 숫자 아닌것들 필터
    name = "" #이름 변수 설정

    flagEntering = False #이름입력창에서 나가는 트리거

    font = pygame.font.SysFont(None, 20, False, False) #폰트 설정 (크기 20)

    nameScrenner = Button(None, name, WHITE, 0, SCRSIZEX//4, SCRSIZEY//4, len(name) * 30, 60)
    nameRule1 = Button(None, "Nickname must be 12 characters or less.", WHITE, 0, SCRSIZEX//4, SCRSIZEY //2, SCRSIZEY * 3 // 4, SCRSIZEY//20)
    nameRule2 = Button(None, "You can't use anything other than English and numbers", WHITE, 0, SCRSIZEX//4, SCRSIZEY//2 + SCRSIZEY//20 ,SCRSIZEY, SCRSIZEY//20)
    

    connecting = Button(None, "Nickname must be 12 characters or less.", WHITE, 0, SCRSIZEX//2, SCRSIZEY //2, SCRSIZEY * 3 // 8, SCRSIZEY//20) #서버 연결 메세지 표시

    connectError = font.render("Fail to connect, shuting down game..", True, [255, 255, 255]) #서버 연결 메세지 표시

    done = False

    while not (flagEntering or done): #먼저 이름을 입력 받은 후 서버와 통신한다.
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN: #키가 눌렸을 때
                if event.key == pygame.K_SPACE: #스페이스면
                    pass #무시
                elif event.key == pygame.K_RETURN: #엔터면
                    if not regularFilter.search(name) and len(name) <= 12: #name함수에 영어나 숫자외 다른게 없고 12자 내면
                        flagEntering = True #반복 중단(다음 단계 진행)
                    else:
                        pass
                
                elif event.key == pygame.K_ESCAPE: #ESC면
                    done = True

                elif event.key == pygame.K_BACKSPACE: #뒤로가기
                    name = name[:-1] #맨 오른쪽 빼고 저장
                else:
                    if len(name) < 12: #12글자 미만일 때만
                        name += event.unicode #쓰기
            
            #이름 지정
            nameScrenner = Button(None, name, WHITE, 0, SCRSIZEX//4, SCRSIZEY//4, len(name) * 30, 60)
        
        screen.fill(BLACK) #검은 화면
        
        #화면에 띄우기
        nameScrenner.displayButton() 
        nameRule1.displayButton()
        nameRule2.displayButton()
        
        pygame.display.flip() #화면 업데이트

    if done:
        return
    
    try : 
        tcpHandler = conTcp(name=name) #tcp 핸들러 시작 (반복문 벗어나면)
        while True:
            screen.fill([0, 0, 0]) #검은 화면

            connecting.displayButton()
            #screen.blit(connecting, (SCRSIZEX // 2, SCRSIZEY // 2)) #대기 메세지 출력

            if(tcpHandler.run()): #run했을때, 실행 완료(True)면
                return #대충 매뉴화면 나오게 하는 함수 (미 구현)
            
            else:
                screen.fill([0, 0, 0]) #검은 화면 (기존 메세지 지우기)
                screen.bilt(connectError, (SCRSIZEX // 2, SCRSIZEY // 2)) #오류 메세지 출력

                
            
            pygame.display.flip()
    except:
        print("서버 연결 오류")

    return
                

def serverRoomList(page):

    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화
    
    global currentundo
    currentundo = lobbyButtons

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #undo 버튼
    
    currentImageList.append(Image( "refresh", SCRSIZEX - SCRSIZEX//20, 0 // 20, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, SCRSIZEX - SCRSIZEX//20, 0, SCRSIZEX // 20, SCRSIZEY // 20, undo)) #새로고침 버튼

    #임시 방 리스트(수정예정)
    roomList = ["dlwodyd", "rlfhrgus", "xlfhrtls", "rlrlrlfhrgus", "dkdlrhsks", "andxoddl", "1", "2", "3", "4", "5", "6"]

    roomCount = len(roomList)

    pageCount = (roomCount - 1) // 5 + 1

    if roomCount == 0: #방이 없네
        pass

    else: #방이 있다
        currentPageRooms = roomList[page * 5 - 5:page * 5 - 1] #현재 페이지의 방 목록 불러오기

        for i in range(len(currentPageRooms)): #현재 페이지의 방 수만큼
            roomName = currentPageRooms[i]
            currentButtonList.append(Button( GRAY,roomName, BLACK, 0, SCRSIZEX // 10, SCRSIZEY // 6 + i * SCRSIZEY // 6, len(roomName) * (SCRSIZEY // 8) // 2, SCRSIZEY // 8)) #undo 버튼

        pass

        








    
def test():
    print("test")
    return



class conTcp():
    def __init__(self, name: str):
        self.name = name #클래스에 이름 저장.
        self.players = []


    def run(self): #연결 실행함수
        self.tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #소켓 생성
        try:
            self.tcpSock.connect((HOST, PORT)) #연결 시작, 요청을 보내고 계속 대기



        except ConnectionRefusedError: #연결 실패시
            return False #연결 실패시, 연결 실패 표시

        return True #연결 되면, 연결 됨 표시
    

    def setName(self, name): #메세지를 받는 핸들러
        self.tcpSock.send(f"0001{name}".encode())
        data = self.tcpSock.recv(1024)
        if(data.decode() == "0080"):
            del data #변수 참조 삭제
            return True #성공 메세지 받을 시
        else:
            del data
            return False
    
    def checkRoomList(self):
        self.tcpSock.send("0002".encode()) #룸 리스트 받기 형식 > 방이름!방이름!
        data = self.tcpSock.recv(1024)
        data = data.decode()
        return data.split("!")
    
    def makeRoom(self, roomCode: str): #방 만들기 (서버 상에서 자동으로 방 참여가 된다.) 이름 규칙 : 12자 내외 영문만
        self.tcpSock.send(f"0003{roomCode}".encode()) #방 생성 요청
        data = self.tcpSock.recv(1024)
        if(data.decode() == "0080"):
            del data #변수 참조 삭제
            return True #성공 메세지 받을 시 >> 클라이언트 측 핸들러에서, 룸 용 함수 실행 필요
        else:
            del data
            return False
        
    def joinRoom(self, roomCode: str): #방 참여요청
        self.tcpSock.send(f"0004{roomCode}".encode()) #방 생성 요청 >> "
        data = self.tcpSock.recv(1024)
        if(data.decode() == "0080"):
            del data #변수 참조 삭제
            return True #성공 메세지 받을 시
        else:
            del data
            return False
        


    def inRoom(self): #방에 접속시 실행됨, 송신 스레드와 수신 스레드가 실행됨
        

    def recvRoom(self): #받는 명령어 핸들러
        data = self.tcpSock.recv(1024).decode()
        if data.startswith("CMD"): #CMD로 시작되는, 서버 설정 메세지인 경우
            cmd = data.split(" ")[1]
            if cmd.startswith("IN"): #누군가 들어왔다는 신호인 경우.
                self.players.append(cmd.replace("IN", "")) #들어온 사람을 플레이어 리스트에 추가.



#------------------------여기부터 시작---------------------------------#

lobbyButtons()

while not done: # loop the game       

    clock.tick(60) #FPS는 60으로

    screen.fill(LIGHTBLUE) #임시 배경색 (차후에 이미지로 변경될수 있음)

    for button in currentButtonList: #버튼들 모두 출력
        button.displayButton()

    for button in currentImageList: #이미지들 모두 출력
        button.displayImage()

    pygame.display.update()

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