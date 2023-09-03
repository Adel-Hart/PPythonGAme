import pygame
from pygame.locals import *
import mapload

import ctypes #컴퓨터 정보, 화면 크기를 가져옴



#아래는 서버용 (ONLY UDP)

import socket


'''
파이썬 게임 개발
! 2023 07 22 start


- 서버 : 김동훈


헷갈리는 것들
RGBlist : 현재 화면 색 (이 화면색과 같은 타일들은 무시됨)

0,0이 맨쪽 위다.

'''

with open("../server/serverip.txt","r") as f:
    HOST = f.readline()
PORT = 8080





class conUdp(): #실제 게임에서 쓰는udp통신, #김동훈 작성
    def __init__(self, players: list, initPos: list, roomName: str, name: str, mapCode: str): #players는 참여자들 닉네임 list, initPos는 플레이할 맵의 플레이어 기본위치
        self.udpSock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #기본 udp 소켓 설정
        self.roomName = roomName
        self.nickName = name
        self.mapCode = mapCode
        self.playerList = {}
        for p in players:
            self.playerList[p] = initPos #플레이어 좌표 초기 설정

        self.rgb = [False, False, False]
        self.done = False



    def runGameScreen(self):
        print("멀티 게임 시작")
        runGame(f"extensionMap/{self.mapCode}.dat", self.playerList.keys())




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
        
        
    






















class pos: # 좌표값 class, 오브젝트마다 pos가 필요해서, 클래스화
    def __init__(self, x, y):
        self.x = x
        self.y = y






clock = pygame.time.Clock() # set fps

COLORON = 150 # 켜질 때의 밝기 이것도 조정가능하게 할거임
#RGB 색상표 사전 지정
WHITE = [COLORON,COLORON,COLORON]
BLACK = [0,0,0]

RED = [COLORON,0,0]
GREEN = [0,COLORON,0]
BLUE = [0,0,COLORON]

YELLOW = [COLORON,COLORON,0]
CYAN = [0,COLORON,COLORON]
MAGENTA = [COLORON,0,COLORON]


WALL = [COLORON//2,COLORON//2,COLORON//2]

RSWITCH = ["switch",1,[True, False, False]]
GSWITCH = ["switch",2,[False, True, False]]
BSWITCH = ["switch",3,[False, False, True]]
YSWITCH = ["switch",4,[True, True, False]]
CSWITCH = ["switch",5,[False, True, True]]
MSWITCH = ["switch",6,[True, False, True]]
WSWITCH = ["switch",7,[True, True, True]]


#해상도 관계없이 플레이 가능하도록, 좌표를 픽셀 기준에서 타일 기준으로 변경 quick fix
#NEWSIZE = 1 #한 타일을 50개로 쪼개서 좌표를 정의한다.

class MovingObject: #MovingObject 객체 생성 : 움직이는 오브젝트, 오브젝트가 여러개가 될 수 있어서 클래스화
    def __init__(self, cx, cy, sx, sy, zx, zy, image): #오브젝트의 기본정보를 지정
        #2차원 공간적 좌표(중심좌표)
        self.coordX = cx
        self.coordY = cy

        #2차원 공간에서의 속도
        self.speedX = sx
        self.speedY = sy

        #크기(직사각형) = 히트박스, 사용할 이미지 파일 : rect
        self.sizeX = zx
        self.sizeY = zy
        self.image = pygame.transform.scale(image, (MAPTILESIZE*zx, MAPTILESIZE*zy))#불러온 이미지의 크기를 타일에 맞춰 조정

        self.realimage = self.image #realimage는 원본image(playerimg)를 변화시키는거라 따로 제작
    def display(self): #화면에 표시
        rect = self.image.get_rect()
        rect.center = (self.coordX*MAPTILESIZE+ORIGINPOINT.x,self.coordY*MAPTILESIZE+ORIGINPOINT.y) #중심좌표 설정
        screen.blit(self.realimage, rect) #스크린에 출력
    
class showImage: #타일, 주인공, 배경을 제외하고 게임 화면에 나올 수 있는 모든 이미지들 
    def __init__(self, cx, cy, zx, zy, image): #이미지의 기본정보를 지정
        #2차원 공간적 좌표(중심좌표)
        self.coordX = cx
        self.coordY = cy
        #크기(직사각형) = 히트박스, 사용할 이미지 파일 : rect
        self.sizeX = zx
        self.sizeY = zy
        self.image = pygame.transform.scale(image, (MAPTILESIZE*zx, MAPTILESIZE*zy))#불러온 이미지의 크기를 타일에 맞춰 조정

        self.realimage = self.image #realimage는 원본image를 변화시키는거라 따로 제작

    def display(self): #화면에 표시
        rect = self.image.get_rect()
        rect.center = (self.coordX*MAPTILESIZE+ORIGINPOINT.x,self.coordY*MAPTILESIZE+ORIGINPOINT.y) #중심좌표 설정
        screen.blit(self.realimage, rect) #스크린에 출력
    


class initMap(): #맵 생성 클래스, 맵이 바뀔수 있어서 클래스화
    def __init__(self, mapName): #맵을 불러오고 각종 상수를 결정한다.
        global TileList, MAPSIZEX, MAPSIZEY, PPOS, GPOS, PSIZEX, PSIZEY, jumpPower, gravity, moveSpeed, backgroundImage
        TileList, MAPSIZEX, MAPSIZEY, PPOS, GPOS ,PSIZEX, PSIZEY, jumpPower, gravity, moveSpeed, backgroundImage = mapload.readMap(mapName) # 맵의 정보 다 받아온다
        global MAPTILESIZE # 한 타일의 길이(픽셀 수)
        MAPTILESIZE = SCRSIZEY // MAPSIZEY if SCRSIZEX//MAPSIZEX > SCRSIZEY//MAPSIZEY else SCRSIZEX // MAPSIZEX #맵의 한 타일이 차지할 픽셀
        
        #만약 해상도가 X축이 길면 짧은 Y축을 기준으로, Y축이 길면 짧은 X축을 기준으로 정사각형의 크기를 지정 (픽셀수를 타일 수로 나눠서 한 타일 당 몇 픽셀인지)

        global mObjects, sImages #표시할 오브젝트, 이미지들 리스트
        mObjects, sImages = [], [] #초기화

        global maincharacter

        playerimg = pygame.image.load("./images/Player.png")

        maincharacter = MovingObject(PPOS.x, PPOS.y, 0, 0, PSIZEX, PSIZEY, playerimg) #MovingObject 주인공을 maincharacter로 선언
        
        mObjects.append(maincharacter) #오브젝트 목록에 추가

        global goal 

        goalimg = pygame.image.load("./images/Goal.png")

        goal = showImage(GPOS.x, GPOS.y, 1, 2, goalimg)

        sImages.append(goal)



        
        global ORIGINPOINT
        #맵의 원점(0,0)의 편향값, 이 값만큼 편향돼서 출력됨으로써 좌우대칭을 맞춘다
        ORIGINPOINT = pos(SCRSIZEX/2-MAPTILESIZE*MAPSIZEX/2, 0) if SCRSIZEX/MAPSIZEX > SCRSIZEY/MAPSIZEY else pos(0,SCRSIZEY/2-MAPTILESIZE*MAPSIZEY/2)
        #만약, 해상도가 X축이 길면, 보류      
        #   
        #TileList = [[BLACK for j in range(self.MAPSIZEY)] for i in range(self.MAPSIZEX)] # 맵 크기만큼의 2차원 배열 생성
        
        #삼항 연산자, 만약 random.randrange(10)이 참 [0이 아니면] BLACK으로, 0일때는(확률이 1/10) 255(coloron)이나 0 중 하나로 만든 색 (0, 0, 0 같은)을 타일로 지정함을 Y만큼 반복 하는걸 X 만큼 반복(2차원 배열 생성)

        global RGBList #현재 화면 상태
        RGBList = [False, False, False] # RGB 모두 켜져 있다

    def displayTiles(self): #타일 그리기
        #타일 그리기
        for y in range(MAPSIZEY):
            for x in range(MAPSIZEX):
                if TileList[x][y][0] == "switch": #스위치일 경우
                    screen.blit(switchImageList[TileList[x][y][1]-1], (x*MAPTILESIZE+ORIGINPOINT.x, y*MAPTILESIZE+ORIGINPOINT.y))

                elif TileList[x][y] == BLACK: #검은색일 경우 출력하지 않기
                    pass
                
                else:
                    imgnumber = 0

                    if TileList[x][y] == RED:
                        imgnumber = 1
                    elif TileList[x][y] == GREEN:
                        imgnumber = 2
                    elif TileList[x][y] == BLUE:
                        imgnumber = 3
                    elif TileList[x][y] == YELLOW:
                        imgnumber = 4
                    elif TileList[x][y] == CYAN:
                        imgnumber = 5
                    elif TileList[x][y] == MAGENTA:
                        imgnumber = 6
                    elif TileList[x][y] == WHITE:
                        imgnumber = 7
                    elif TileList[x][y] == WALL:
                        imgnumber = 8
                    else:
                        pass
                    
                    if isWall(TileList[x][y]):
                        screen.blit(tileImageList[imgnumber], (x*MAPTILESIZE+ORIGINPOINT.x, y*MAPTILESIZE+ORIGINPOINT.y))
                    else:
                        screen.blit(alphatileImageList[imgnumber], (x*MAPTILESIZE+ORIGINPOINT.x, y*MAPTILESIZE+ORIGINPOINT.y))
                    
                    
    #pygame.draw.rect(화면크기, 색[rgbTile이라는 타일에대한 색 정보에서 해당 타일 색을 가져옴], [x위치(한 열마다, 타일의 크기를 곱하면, 타일의 위치가 나옴 혹시 모를 편차 때문에 수정된 원점(왼쪽 위)를 더해서 수정), y위치, x크기, y크기])
    

    def RGBTile(self, x, y):
        if TileList[x][y] == WALL: # 벽의 색 어중간한 색으로 조정
            properTile = list(TileList[x][y]) # 임시 타일
            for i in range(3): # R G B 에 대해          
                if RGBList[i]: #RGBList에서는 켜져있다면
                    properTile[i] = (properTile[i]+COLORON)//2 # 색깔의 평균값 대입
            return properTile
            #추가 설명, map(함수, 값) 값들이 함수로 가 함수대로 변형, 즉 RGBList의 값들이 lamda에 x가 되어 바뀌어 나온다.
        else: 
            return TileList[x][y] # 색이 있을시 원래 색으로 출력

    def drawGrids(self): # 그리드 그리기
        GRIDCOLOR = WALL
        for x in range(MAPSIZEX):
            pygame.draw.line(screen, GRIDCOLOR, [x*MAPTILESIZE+ORIGINPOINT.x,ORIGINPOINT.y], [x*MAPTILESIZE+ORIGINPOINT.x,MAPSIZEY*MAPTILESIZE+ORIGINPOINT.y])
        for y in range(MAPSIZEY):
            pygame.draw.line(screen, GRIDCOLOR, [ORIGINPOINT.x,y*MAPTILESIZE+ORIGINPOINT.y], [MAPSIZEX*MAPTILESIZE+ORIGINPOINT.x,y*MAPTILESIZE+ORIGINPOINT.y])



'''
김동훈 프로토 타입
'''

def isWall(COLOR): # 그 색깔이 벽이면 True 아니면 False
    if COLOR[0] == "switch": #스위치는 벽이 아님
        return False
    elif COLOR == BLACK: # 검은색일 경우
        return False
    elif COLOR == list(map(lambda x: COLORON if x else 0, RGBList)): # 배경색과 같을 경우
        return False
    return True # 배경색과 다를 경우


def changeRGB(changedRGB): #RGB 변경 시
    global backImage  
    RGBList[changedRGB] = not RGBList[changedRGB]
    imgnumber = 8

    if RGBList == [0,0,0]:
        imgnumber = 0
    elif RGBList == [1,0,0]:
        imgnumber = 1
    elif RGBList == [0,1,0]:
        imgnumber = 2
    elif RGBList == [0,0,1]:
        imgnumber = 3
    elif RGBList == [1,1,0]:
        imgnumber = 4
    elif RGBList == [0,1,1]:
        imgnumber = 5
    elif RGBList == [1,0,1]:
        imgnumber = 6
    elif RGBList == [1,1,1]:
        imgnumber = 7
    else:
        pass
    
    backImage = pygame.transform.scale(pygame.image.load(f"./images/backgrounds/{backgroundImage}/colors/{imgnumber}.png"), (MAPTILESIZE*MAPSIZEX, MAPTILESIZE*MAPSIZEY))













def onGround(object): #바닥에 붙어있는지 여부 판정
    if checkEscapeY(object): #맵탈출이라면
        return False
    xLeft = object.coordX - object.sizeX/2
    xRight = object.coordX + object.sizeX/2
    y = object.coordY + object.sizeY/2+0.01
    return findWall(xLeft,xRight,y,y)[0]
        

def findWall(xLeft, xRight, yUp, yDown): # 지정한 범위 안쪽에 벽이 있으면 True, 없으면 False 그 벽의 좌표를 List로 반환
    xStart = int(xLeft+0.001)
    xEnd = int(xRight-0.001)
    yStart = int(yUp+0.001)
    yEnd = int(yDown-0.001)
    if xStart < 0:
        xStart = 0
    elif xEnd >= MAPSIZEX:
        xEnd = MAPSIZEX-1

    if yStart < 0:
        yStart = 0
    elif yEnd >= MAPSIZEY:
        yEnd = MAPSIZEY-1

    for x in range(xStart, xEnd+1): # x범위
        for y in range(yStart, yEnd+1): # y범위
            if isWall(TileList[x][y]): 
                return [True, [x,y]]
    return [False,[]]

def activateSwitch(pos:pos): #스위치라면 발동시킨다
    if TileList[pos.x][pos.y][0] == "switch": #그 좌표의 타일이 스위치라면
        #print("switch", pos.x, pos.y)
        for i in range(3): #R, G, B 마다 한번씩
            if TileList[pos.x][pos.y][2][i]: #스위치에 해당한다면
                changeRGB(i) #RGB값중 하나 변경 

def findSwitch(object:MovingObject): # 지정한 범위 안쪽에 스위치가 있으면 ~
    xStart = int(object.coordX-object.sizeX/2+0.1)
    xEnd = int(object.coordX+object.sizeX/2-0.1)

    yStart = int(object.coordY-object.sizeY/2+0.1)
    yEnd = int(object.coordY+object.sizeY/2-0.1)

    for x in range(xStart, xEnd+1): # x범위
        for y in range(yStart, yEnd+1): # y범위
            #print(x, y)
            activateSwitch(pos(x,y)) 
                
    return



def checkClip(object): # 오브젝트가 꼈는지 확인
    return findWall(object.coordX - object.sizeX/2, object.coordX + object.sizeX/2, object.coordY - object.sizeY/2, object.coordY + object.sizeY/2)[0]
def moveObjects(): # 움직이는 오브젝트 이동
    for object in mObjects: # 모든 움직이는 오브젝트 불러오기

        '''
        벽충돌 판정법
        1. 이동 후의 좌표를 구한다
        2. 그 좌표에서 오브젝트의 크기만큼 왼쪽 위, 오른쪽 아래로 범위를 확장한다
        3. 그 범위 안쪽에 있는 타일을 모두 검사한다
        4. 만약 그중에 벽 타일이 있다면 이동을 실패하고 속력을 0으로 한다.
        '''

        
        if object.speedX != 0: # 속도만큼 x좌표 이동하기

            nextX = object.coordX + object.speedX # 이동 후의 X좌표
            # 총 크기를 계산 후 타일 기준으로 환산
            xLeft = nextX - object.sizeX/2
            xRight = nextX + object.sizeX/2
            yUp = object.coordY - object.sizeY/2
            yDown = object.coordY + object.sizeY/2
                
            if findWall(xLeft, xRight, yUp, yDown)[0]: # 충돌 시 속도 0으로
                object.speedX = 0
            else: # 충돌 아니라면 이동
                object.coordX += object.speedX 

        if object.speedY != 0: # 속도만큼 y좌표 이동하기

            nextY = object.coordY + object.speedY # 이동 후의 Y좌표

            # 총 크기를 계산 후 타일 기준으로 환산
            xLeft = object.coordX - object.sizeX/2
            xRight = object.coordX + object.sizeX/2
            yUp = nextY - object.sizeY/2
            yDown = nextY + object.sizeY/2   
            if findWall(xLeft, xRight, yUp, yDown)[0]:
                if object.speedY > 0: # 바닥에 막힐 경우
                    object.speedY = 0
                    object.coordY = findWall(xLeft, xRight, yUp, yDown)[1][1] - object.sizeY/2 # 바닥에 딱 붙이기
                elif object.speedY < 0: # 천장에 막힐 경우
                    object.coordY = (findWall(xLeft, xRight, yUp, yDown)[1][1]+1) + object.sizeY/2 # 천장에 딱 붙이기
                    object.speedY = 0
                
            object.coordY += object.speedY 

def gravityObjects(): #중력 적용
    for object in mObjects: # 모든 움직이는 오브젝트 불러오기     
        if onGround(object) == False: # 공중에 있다면?
            object.speedY += gravity # y속도에 중력값을 더한다

def checkEscapeY(object): # 속도까지 고려한 Y방향 맵탈출 여부 True or False
    if object.coordY+object.speedY+object.sizeY/2 >= MAPSIZEY:
        return True
    elif object.coordY+object.speedY-object.sizeY/2 < 0:
        return True
    return False

def checkObjectEscape(object): #오브젝트가 현재 맵을 탈출했는지 판단 True or False
    if object.coordY+object.sizeY/2 >= MAPSIZEY:
        return True
    if object.coordY-object.sizeY/2 < 0:
        return True
    if object.coordX+object.sizeX/2 >= MAPSIZEX:
        return True
    if object.coordX-object.sizeX/2 < 0:
        return True
    return False

def isCollapse(object1, object2): #movingObject 또는 showImage 2개가 겹쳐있는지 여부 True or False
    if object1.coordX - object1.sizeX - object2.sizeX < object2.coordX < object1.coordX + object1.sizeX + object2.sizeX and\
    object1.coordY - object1.sizeY - object2.sizeY < object2.coordY < object1.coordY + object1.sizeY + object2.sizeY:
        #한 직사각형의 중심좌표를 중심으로 두 사각형의 x, y 길이를 합한 새로운 직사각형을 만든다.
        #그 직사각형 안에 나머지 직사각형의 중심좌표가 들어있다면, 두 직사각형은 겹쳐있었다는 결론을 얻을 수 있다.
        return True
    else:
        return False
 


def runGame(mapName, otherPlayers:list = None): # 게임 실행 함수

    user32 = ctypes.windll.user32
    global SCRSIZEX, SCRSIZEY
    SCRSIZEX = user32.GetSystemMetrics(0) #화면의 해상도 (픽셀수) 구하기 가로
    SCRSIZEY = user32.GetSystemMetrics(1) #세로

    size = [SCRSIZEX, SCRSIZEY] # set screen size
    global screen
    screen = pygame.display.set_mode(size) # set pygame screen to object "screen"

    global clear
    clear = False

    global done 
    done = False
    pygame.display.set_caption(str(mapName)) # set window's name a mapName

    global wantToMoveX
    wantToMoveX = 0 # 플레이어가 누르고 있는 X방향(-1, 1)

    global wantToJump # 위 방향키를 누르고 있는지 여부(True, False)

    wantToJump = False

    try:
        Map = initMap(mapName)
    except:
        print(str(mapName)+ "로딩 실패")
        return
    
    print(str(mapName)+" 로딩 완료")
    

    #맵이 바뀌기 때문에, 맵 인스턴스 생성

    

    if otherPlayers != None: #다른 플레이어가 있다면
        playerImageList = []
        playerImageList.append(showImage(PPOS.x, PPOS.y, PSIZEX, PSIZEY, "./images/Player.png")) 
    
    screen.fill(WHITE) # 화면 리셋
    
    #배경 이미지 설정
    global backImage
    backImage = pygame.transform.scale(pygame.image.load(f"./images/backgrounds/{backgroundImage}/colors/{0}.png"), (MAPTILESIZE*MAPSIZEX, MAPTILESIZE*MAPSIZEY))
    
    global tileImageList
    tileImageList = []

    for i in range(9): #타일 색깔별 이미지 리스트
        tileImageList.append(pygame.transform.scale(pygame.image.load(f"./images/tiles/colors/{i}.png"), (MAPTILESIZE+1, MAPTILESIZE+1))) #크기 조정
    
    global alphatileImageList
    alphatileImageList = []

    for i in range(9): #반투명한 타일 색깔별 이미지 리스트
        temp = pygame.image.load(f"./images/tiles/colors/{i}.png")
        temp.set_alpha(128)
        alphatileImageList.append(pygame.transform.scale(temp, (MAPTILESIZE+1, MAPTILESIZE+1))) #크기 조정
    
    global switchImageList #스위치 이미지 리스트 [0]은 OFF, [1]은 ON
    switchImageList = []
    for i in range(1,8):
        temp = pygame.image.load(f"./images/switch/{i}.png")
        if i == 7:
            temp.set_colorkey((0,0,0))
        else:
            temp.set_colorkey((255, 255, 255))
        switchImageList.append(pygame.transform.scale(temp, (MAPTILESIZE+1, MAPTILESIZE+1))) #크기 조정

    

    while not done: # loop the game

        clock.tick(60) # FPS 적용
        

        #배경사진 출력
        
        screen.blit(backImage, (ORIGINPOINT.x, ORIGINPOINT.y))
        
        Map.displayTiles() # 타일 모두 출력

        Map.drawGrids() # 그리드 그리기

        gravityObjects() #중력 적용
    
        moveObjects() # 움직이는 오브젝트 일괄 이동

        for image in sImages: # 모든 이미지 불러오기 
            image.display() # 이미지 일괄 출력

        for object in mObjects: # 모든 움직이는 오브젝트 불러오기 
            object.display() # 움직이는 오브젝트 일괄 출력
            
            
        pygame.display.update()

        #print(maincharacter.coordX,maincharacter.coordY)

        if checkObjectEscape(maincharacter): # y방향 맵탈출시 사망판정
            gameOver()

        if checkClip(maincharacter): # 오브젝트에 낄시 사망판정
            gameOver()
        
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 종료 이벤트
                clear = 2
                done=True

            if event.type == pygame.KEYUP: # 방향키 뗴기
                if event.key == pygame.K_LEFT and wantToMoveX == -1:
                    wantToMoveX = 0

                elif event.key == pygame.K_RIGHT and wantToMoveX == 1:
                    wantToMoveX = 0

                if event.key == pygame.K_UP and wantToJump == 1:
                    wantToJump = False

                elif event.key == pygame.K_DOWN:
                    pass

            if event.type == pygame.KEYDOWN: # 방향키 누르기
                if event.key == pygame.K_LEFT:
                    wantToMoveX = -1
                    maincharacter.realimage = pygame.transform.flip(maincharacter.image,True,False)

                elif event.key == pygame.K_RIGHT:
                    wantToMoveX = 1
                    maincharacter.realimage = maincharacter.image
                
                if event.key == pygame.K_UP:
                    wantToJump = True

                elif event.key == pygame.K_DOWN:
                    pass

                if event.key == pygame.K_ESCAPE: # 직접 중단하는 키
                    clear = 2
                    done = True 
                
                if event.key == pygame.K_z: #상호작용 키
                    if isCollapse(maincharacter, goal): #도착 지점에 있다면
                        gameClear()
                    else:
                        findSwitch(maincharacter)

                if event.key == pygame.K_r: # R 변경
                    changeRGB(0)
                elif event.key == pygame.K_g: # G 변경
                    changeRGB(1)
                elif event.key == pygame.K_b: # B 변경
                    changeRGB(2)

        maincharacter.speedX = wantToMoveX*moveSpeed # 이동속도만큼 X좌표 속도 설정

        if wantToJump and onGround(maincharacter) and maincharacter.speedY == 0: #점프하고 싶다면 바닥에 있으며 y속도가 0이여야 한다
            maincharacter.speedY = -1 * jumpPower
    
    #while문 탈출 : 게임 종료
    if clear > 0: #사망한 경우가 아니라면
        font = pygame.font.SysFont("Consolas", 200) #폰트 설정
        img = font.render("CLEARED! PLEASE GO BACK TO EDITOR!", True, RED) #렌더
        img = pygame.transform.scale(img, (SCRSIZEX//2, SCRSIZEX//20))
        screen.blit(img, (0,0)) #텍스트 표시

        pygame.display.update()

    return clear #클리어 여부를 반환 

def gameClear(): #클리어=도착시
    print("도착")
    global clear
    clear = 1
    global done
    done = True

def gameOver(): # 사망시
    print("사망")
    clear = 0
    global done
    done = True
