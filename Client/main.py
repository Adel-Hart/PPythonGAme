import pygame
import os
import math
import random
import time



'''
파이썬 게임 개발
! 2023 07 22 start


-김동훈


'''


pygame.init() # initialize pygame

#맵의 크기 지정
MAPSIZEX = 25
MAPSIZEY = 15

MAPTILESIZE = 40 #맵의 한 타일이 차지할 픽셀

size = [MAPSIZEX*MAPTILESIZE, MAPSIZEY*MAPTILESIZE] # set screen size
screen = pygame.display.set_mode(size) # set pygame screen to object "screen"

pygame.display.set_caption("AL1S") # set window's name a "AL1s" (quick fix)

done = False # set shutdown triger

clock = pygame.time.Clock() # set fps

#RGB 색상표 사전 지정
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)


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

mainchracter = MovingObject(MAPSIZEX/2, MAPSIZEY/2, 0, 0, 2, 2, blockimg) #MovingObject 주인공을 mainchracter로 선언

mObjects.append(mainchracter) #오브젝트 목록에 추가


global TileList # Tile의 집합, 즉 맵
TileList = [[BLACK for j in range(MAPSIZEY)] for i in range(MAPSIZEX)] # 맵 크기만큼의 2차원 배열 생성

WallList = [WHITE] # Tile의 색상 중 벽으로 간주될 색상(RGB에 따라 변경할 예정 )

for i in range(MAPSIZEX):
    TileList[i][MAPSIZEY-1] = WHITE

def displayTiles(): #타일 그리기
    for y in range(MAPSIZEY):
        for x in range(MAPSIZEX):
            pygame.draw.rect(screen, TileList[x][y], [x*MAPTILESIZE,y*MAPTILESIZE,MAPTILESIZE,MAPTILESIZE]) # 정사각형으로 타일 색칠


def drawGrids(): # 그리드 그리기
    for x in range(MAPSIZEX):
        pygame.draw.line(screen, WHITE, [x*MAPTILESIZE,0], [x*MAPTILESIZE,MAPSIZEY*MAPTILESIZE])
    for y in range(MAPSIZEY):
        pygame.draw.line(screen, WHITE, [0,y*MAPTILESIZE], [MAPSIZEX*MAPTILESIZE,y*MAPTILESIZE])

def onGround(object): #바닥에 붙어있는지 여부 판정
    xLeft = object.coordX - object.sizeX/2
    xRight = object.coordX + object.sizeX/2
    y = object.coordY + object.sizeY/2+0.01
    return findWall(xLeft,xRight,y,y)

def displayMovingObjects():# 움직이는 오브젝트 표시
    for object in mObjects: # 모든 움직이는 오브젝트 불러오기

        rect = object.image.get_rect() 
        rect.center = (object.coordX,object.coordY) #중심좌표 설정

        screen.blit(object.image, rect) #스크린에 출력

def findWall(xLeft, xRight, yUp, yDown): # 지정한 범위 안쪽에 벽이 있으면 True, 없으면 False 반환
    for x in range(int(xLeft // MAPTILESIZE), int((xRight-0.001) // MAPTILESIZE)+1): # x범위
        for y in range(int(yUp // MAPTILESIZE), int((yDown-0.001) // MAPTILESIZE)+1): # y범위
            if WallList.count(TileList[x][y]) >= 1: 
                return True
    return False

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
            elif findWall(xLeft, xRight, yUp, yDown): # 충돌 시 속도 0으로
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
            elif findWall(xLeft, xRight, yUp, yDown): # 충돌 시 속도 0으로
                object.speedY = 0
            else: # 충돌 아니라면 이동
                object.coordY += object.speedY 

global gravity
gravity = 0.4 #중력가속도
global jumpPower
jumpPower = 10 #점프 가속도
def gravityObjects(): #중력 적용
    for object in mObjects: # 모든 움직이는 오브젝트 불러오기
        if onGround(object) == False: # 공중에 있다면?
            object.speedY += gravity # y속도에 중력값을 더한다



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
        
        print(onGround(mainchracter), mainchracter.speedY)

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
            
            
        
        mainchracter.speedX = wantToMoveX*moveSpeed*MAPTILESIZE # 이동속도만큼 X좌표 속도 설정

        
        if wantToJump and onGround(mainchracter) and mainchracter.speedY == 0: #점프하고 싶다면 바닥에 있으며 y속도가 0이여야 한다
            print("JUMP!")
            mainchracter.speedY = -1 * jumpPower


        pygame.display.update()
 
runGame() 
pygame.quit() #게임 종료

