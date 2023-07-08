import pygame
from pygame.locals import *
import os
import math
import random
import time

import ctypes #컴퓨터 정보, 화면 크기를 가져옴


'''
파이썬 게임 개발
! 2023 07 22 start


-김동훈


'''
'''

pygame.init() # initialize pygame

def setScreen():


'''




user32 = ctypes.windll.user32
SCRSIZEX = user32.GetSystemMetrics(0) #화면의 해상도 (픽셀수) 구하기
SCRSIZEY = user32.GetSystemMetrics(1)





#맵의 크기 지정 (총 타일 개수!!!!)
MAPSIZEX = 40 
MAPSIZEY = 10

MAPTILESIZE = SCRSIZEY // MAPSIZEY if SCRSIZEX/MAPSIZEX > SCRSIZEY/MAPSIZEY else SCRSIZEX // MAPSIZEX #맵의 한 타일이 차지할 픽셀
#만약 해상도가 X축이 길면 짧은 Y축을 기준으로, Y축이 길면 짧은 X축을 기준으로 정사각형의 크기를 지정 (픽셀수를 타일 수로 나눠서 한 타일 당 몇 픽셀인지)

class pos: # 좌표값 class
    def __init__(self, x, y):
        self.x = x
        self.y = y

#맵의 원점(0,0)의 편향값, 이 값만큼 편향돼서 출력됨으로써 좌우대칭을 맞춘다
ORIGINPOINT = pos(SCRSIZEX/2-MAPTILESIZE*MAPSIZEX/2, 0) if SCRSIZEX/MAPSIZEX > SCRSIZEY/MAPSIZEY else pos(0,SCRSIZEY/2-MAPTILESIZE*MAPSIZEY/2)



size = [SCRSIZEX, SCRSIZEY] # set screen size
screen = pygame.display.set_mode(size) # set pygame screen to object "screen"

pygame.display.set_caption("AL1S") # set window's name a "AL1s" (quick fix)

done = False # set shutdown triger

clock = pygame.time.Clock() # set fps

COLORON = 255 # 켜질 때의 색상
COLOROFF = 90
#RGB 색상표 사전 지정
WHITE = [COLORON,COLORON,COLORON]
BLACK = [0,0,0]
GRAY = [COLOROFF,COLOROFF,COLOROFF]

RED = [COLORON,0,0]
GREEN = [0,COLORON,0]
BLUE = [0,0,COLORON]

YELLOW = [COLORON,COLORON,0]
MAGENTA = [COLORON,0,COLORON]
CYAN = [0,COLORON,COLORON]

WALL = [150,150,150]

COLORLIST = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE] # 모든 색상의 리스트





class MovingObject: #MovingObject 객체 생성 : 움직이는 오브젝트
    def __init__(self, cx, cy, sx, sy, zx, zy, image): #오브젝트의 기본정보를 지정
        #2차원 공간적 좌표(중심좌표)
        self.coordX = MAPTILESIZE*cx
        self.coordY = MAPTILESIZE*cy

        #2차원 공간에서의 속도
        self.speedX = sx
        self.speedY = sy

        #크기(직사각형) = 히트박스, 사용할 이미지 파일 : rect
        self.sizeX = MAPTILESIZE*zx
        self.sizeY = MAPTILESIZE*zy
        self.image = pygame.transform.scale(image, (MAPTILESIZE*zx, MAPTILESIZE*zy))#불러온 이미지의 크기를 타일에 맞춰 조정


blockimg = pygame.image.load("./images/Block.jpg") #테스트용 임시 이미지

mObjects = [] #움직이는 오브젝트 리스트

maincharacter = MovingObject(3, 4, 0, 0, 1.5, 2.5, blockimg) #MovingObject 주인공을 maincharacter로 선언

mObjects.append(maincharacter) #오브젝트 목록에 추가


global TileList # Tile의 집합, 즉 맵
TileList = [[BLACK if random.randrange(10) else [[COLORON,0][random.randrange(2)],[COLORON,0][random.randrange(2)],[COLORON,0][random.randrange(2)]] for j in range(MAPSIZEY)] for i in range(MAPSIZEX)] # 맵 크기만큼의 2차원 배열 생성
#삼항 연산자, 만약 random.randrange(10)이 참 [0이 아니면] BLACK으로, 0일때는(확률이 1/10) 255(coloron)이나 0 중 하나로 만든 색 (0, 0, 0 같은)을 타일로 지정함을 Y만큼 반복 하는걸 X 만큼 반복(2차원 배열 생성)




for i in range(MAPSIZEX): #바닥 채우기
    TileList[i][MAPSIZEY-1] = WALL

for i in range(MAPSIZEX): #천장 채우기
    TileList[i][0] = BLACK


def displayTiles(): #타일 그리기
    for y in range(MAPSIZEY):
        for x in range(MAPSIZEX):
            pygame.draw.rect(screen, RGBTile(x,y), [x*MAPTILESIZE+ORIGINPOINT.x,y*MAPTILESIZE+ORIGINPOINT.y,MAPTILESIZE,MAPTILESIZE]) # 정사각형으로 타일 색칠

global RGBList
RGBList = [False, False, False] # RGB 모두 켜져 있다

def RGBTile(x, y):
    if TileList[x][y] == WHITE:
        if RGBList == [False,False,False]: # 하얀색이고 모두 꺼져있다면
            return GRAY
        else:
            return WHITE
    elif TileList[x][y] == BLACK:
        return BLACK
    else:       
        properTile = list(TileList[x][y]) # 임시 타일
        for i in range(3): # R G B 에 대해          
            if properTile[i] == COLORON: # 그 타일에 포함된 색상이라면
                if RGBList[i] == False: #RGBList에서는 꺼져있고 타일에서는 켜져있다면
                    properTile[i] = COLOROFF # 끈다
        return properTile

def isWall(COLOR): # 그 색깔이 벽이면 True 아니면 False
    if COLOR == WALL: # 벽으로 지정된 색깔
        return True
    for i in range(3): # R G B 에 대해 
        if COLOR[i] == COLORON and RGBList[i]: # 켜져있는 색깔이 있다면
            return True
    return False # 다 꺼져있다면

def changeRGB(changedRGB): #RGB 변경 시
    RGBList[changedRGB] = not RGBList[changedRGB]
    print(RGBList)




'''
김동훈 프로토 타입
'''











def drawGrids(): # 그리드 그리기
    for x in range(MAPSIZEX):
        pygame.draw.line(screen, WHITE, [x*MAPTILESIZE+ORIGINPOINT.x,ORIGINPOINT.y], [x*MAPTILESIZE+ORIGINPOINT.x,MAPSIZEY*MAPTILESIZE+ORIGINPOINT.y])
    for y in range(MAPSIZEY):
        pygame.draw.line(screen, WHITE, [ORIGINPOINT.x,y*MAPTILESIZE+ORIGINPOINT.y], [MAPSIZEX*MAPTILESIZE+ORIGINPOINT.x,y*MAPTILESIZE+ORIGINPOINT.y])

def onGround(object): #바닥에 붙어있는지 여부 판정
    if checkEscapeY(object): #맵탈출이라면
        return False
    xLeft = object.coordX - object.sizeX/2
    xRight = object.coordX + object.sizeX/2
    y = object.coordY + object.sizeY/2+0.01
    return findWall(xLeft,xRight,y,y)[0]

def displayMovingObjects():# 움직이는 오브젝트 표시
    for object in mObjects: # 모든 움직이는 오브젝트 불러오기

        rect = object.image.get_rect() 
        rect.center = (object.coordX+ORIGINPOINT.x,object.coordY+ORIGINPOINT.y) #중심좌표 설정

        screen.blit(object.image, rect) #스크린에 출력

def findWall(xLeft, xRight, yUp, yDown): # 지정한 범위 안쪽에 벽이 있으면 True, 없으면 False 그 벽의 좌표를 List로 반환
    xStart = int(xLeft // MAPTILESIZE)
    xEnd = int((xRight-0.001) // MAPTILESIZE)
    yStart = int(yUp // MAPTILESIZE)
    yEnd = int((yDown-0.001) // MAPTILESIZE)

    if xStart < 0:
        xStart = 0
    elif xEnd >= MAPSIZEX:
        xEnd = MAPSIZEX-1
    elif yStart < 0:
        yStart = 0
    elif yEnd >= MAPSIZEX:
        yEnd = MAPSIZEX-1

    for x in range(xStart, xEnd+1): # x범위
        for y in range(yStart, yEnd+1): # y범위
            if isWall(TileList[x][y]): 
                return [True, [x,y]]
    return [False,[]]

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
                
            if nextX - object.sizeX/2 < 0 or nextX + object.sizeX/2 > MAPTILESIZE*MAPSIZEX: # 맵탈출 여부
                object.speedX = 0
            elif findWall(xLeft, xRight, yUp, yDown)[0]: # 충돌 시 속도 0으로
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
            
            if nextY - object.sizeY/2 < 0 or nextY + object.sizeY/2 > MAPTILESIZE*MAPSIZEY: # 맵탈출 여부
                object.speedY = 0               
            elif findWall(xLeft, xRight, yUp, yDown)[0]:
                if object.speedY > 0: # 바닥에 막힐 경우
                    print("바닥")
                    object.coordY = findWall(xLeft, xRight, yUp, yDown)[1][1]*MAPTILESIZE - object.sizeY/2 # 바닥에 딱 붙이기
                elif object.speedY < 0: # 천장에 막힐 경우
                    print("천장")
                    object.coordY = (findWall(xLeft, xRight, yUp, yDown)[1][1]+1)*MAPTILESIZE + object.sizeY/2 # 바닥에 딱 붙이기
                object.speedY = 0
            else: # 충돌 아니라면 이동
                object.coordY += object.speedY 

global gravity
gravity = 0.02 #중력가속도
global jumpPower
jumpPower = 0.5 #점프 가속도

def gravityObjects(): #중력 적용
    for object in mObjects: # 모든 움직이는 오브젝트 불러오기     
        if checkEscapeY(object):# 맵탈출이라면
            object.speedY = 0
        elif onGround(object) == False: # 공중에 있다면?
            object.speedY += gravity * MAPTILESIZE # y속도에 중력값을 더한다

def checkEscapeY(object): # Y방향 맵탈출 여부 True or False
    if object.coordY+object.speedY+object.sizeY/2 >= MAPTILESIZE*MAPSIZEY:
        return True
    elif object.coordY+object.speedY-object.sizeY/2 < 0:
        return True
    return False

def runGame(): # 게임 실행 함수

    global done #종료 트리거

    global moveSpeed
    moveSpeed = 0.25 # 프레임당 이동할 타일 수(=속도)

    global wantToMoveX
    wantToMoveX = 0 # 플레이어가 누르고 있는 X방향(-1, 1)

    global wantToJump # 위 방향키를 누르고 있는지 여부(True, False)
    wantToJump = False

    while not done: # loop the game
        clock.tick(60) # ! must multiply fps to move speed (cause difference of speed) !
       
        screen.fill(WHITE) # 배경색

        displayTiles() # 타일 모두 출력

        drawGrids() # 그리드 그리기

        displayMovingObjects() # 움직이는 오브젝트 일괄 출력

        gravityObjects() #중력 적용
    
        moveObjects() # 움직이는 오브젝트 일괄 이동

        if checkClip(maincharacter): # 오브젝트에 낄시 사망판정
            gameOver()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 종료 이벤트
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

                elif event.key == pygame.K_RIGHT:
                    wantToMoveX = 1
                
                if event.key == pygame.K_UP:
                    wantToJump = True

                elif event.key == pygame.K_DOWN:
                    pass

                if event.key == pygame.K_r: # R 변경
                    changeRGB(0)
                elif event.key == pygame.K_g: # G 변경
                    changeRGB(1)
                elif event.key == pygame.K_b: # B 변경
                    changeRGB(2)
            
        
        maincharacter.speedX = wantToMoveX*moveSpeed*MAPTILESIZE # 이동속도만큼 X좌표 속도 설정

        
        if wantToJump and onGround(maincharacter) and maincharacter.speedY == 0: #점프하고 싶다면 바닥에 있으며 y속도가 0이여야 한다
            print("JUMP!")
            maincharacter.speedY = -1 * jumpPower * MAPTILESIZE


        pygame.display.update()

def gameOver(): # 사망시
    print("사망")
    global done
    done = True

runGame() 
pygame.quit() #게임 종료

