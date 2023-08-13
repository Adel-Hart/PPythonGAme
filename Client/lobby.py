import main
import pygame
import ctypes

def darkColor(color): #색을 더 어둡게 
    return list(map(lambda x: x / 2, color)) #RGB 값을 모두 절반으로

class Image:
    def __init__(self, imageName:str, posX :int, posY:int, width:int, height:int):    

        self.image = pygame.transform.scale(pygame.image.load(f"./images/lobby/{imageName}.png"), (width, height))

        self.posX = posX
        self.posY = posY
        return
    def displayImage(self):
        screen.blit(self.image, (self.posX, self.posY))

class Button: #로비에서 클릭이벤트가 있을때 검사할 버튼 객체
    def __init__(self, backColor, text : str, textColor, marginx:int ,posX :int, posY:int, width:int, height:int, function = None): 
        # backColor: 버튼의 색상
        # text, textColor: 버튼에 표시될 문자열, 그 색상
        # marginx = text의 x방향 여백
        # posX,posY: 버튼위 왼쪽위 좌표
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


        return

    def checkMouse(self): # 마우스가 버튼 위에 있는지 여부 반환

        mousePos = pygame.mouse.get_pos() # 마우스 좌표

        if self.posX + self.width > mousePos[0] > self.posX and self.posY + self.height > mousePos[1] > self.posY and self.function != None: #마우스의 위치가 버튼 안쪽이라면
            return True
        else:
            return False
    
    def displayButton(self): #버튼 표시
        
        if self.checkMouse(): #마우스의 위치가 버튼 안쪽이라면
            pygame.draw.rect(screen, darkColor(self.backColor), [self.posX, self.posY, self.width, self.height]) #좀더 어둡게 버튼 색상 변경
        else:
            pygame.draw.rect(screen, self.backColor, [self.posX, self.posY, self.width, self.height]) #기본 버튼 색상
        
        

        font = pygame.font.SysFont("None", 200) #폰트 설정
        img = font.render(self.text, True, self.textColor) #렌더
        img = pygame.transform.scale(img, (self.width - self.marginx*2, self.height))
        screen.blit(img, (self.posX+self.marginx,self.posY)) #텍스트 표시
    
    def checkFunction(self): #함수 실행
        if self.checkMouse() and self.function != None:
            self.function()

currentImageList = []# 현재 사용중인 이미지의 리스트
currentButtonList = [] # 현재 사용중인 버튼의 리스트

pygame.init() # initialize pygame

clock = pygame.time.Clock() #FPS 설정

done = False #pygame 종료용 트리거

user32 = ctypes.windll.user32

SCRSIZEX = user32.GetSystemMetrics(0) #화면의 해상도 (픽셀수) 구하기 가로
SCRSIZEY = user32.GetSystemMetrics(1) #세로

size = [SCRSIZEX, SCRSIZEY] # set screen size

screen = pygame.display.set_mode(size) # set pygame screen to object "screen"

WHITE = [255, 255, 255]
GRAY = [127, 127, 127]
BLACK = [0,0,0]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]

def quit(): #종료함수
    global done
    done = True
    return

def lobbyButtons(): #처음 시작 장면 
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    currentButtonList.append(Button( BLACK,"SINGLE PLAYER", WHITE, SCRSIZEX // 21, SCRSIZEX // 3, SCRSIZEY // 2, SCRSIZEX // 3, SCRSIZEY * 3 // 40, singleButtons))
    currentButtonList.append(Button( BLACK,"MULTI PLAYER", WHITE, SCRSIZEX // 21, SCRSIZEX // 3, SCRSIZEY * 5 // 8 , SCRSIZEX // 3, SCRSIZEY * 3 // 40, test))
    currentButtonList.append(Button( BLACK,"SETTINGS", WHITE, SCRSIZEX // 14, SCRSIZEX // 3, SCRSIZEY *3 // 4, SCRSIZEX // 3, SCRSIZEY * 3 // 40, test))
    currentButtonList.append(Button( BLACK,"QUIT", WHITE, SCRSIZEX // 9, SCRSIZEX // 3, SCRSIZEY * 7 // 8, SCRSIZEX // 3, SCRSIZEY * 3 // 40, quit))
    return

def singleButtons(): #싱글플레이
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    currentImageList.append(Image("story", SCRSIZEX // 5 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))
    currentImageList.append(Image("custom", SCRSIZEX * 11 // 20 , SCRSIZEY // 6,  SCRSIZEX // 4, SCRSIZEY // 2 ))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, lobbyButtons)) #undo 버튼

    currentButtonList.append(Button( BLACK,"STORY", WHITE, SCRSIZEX // 21, SCRSIZEX // 5, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, storyButtons))
    currentButtonList.append(Button( BLACK,"CUSTOM", WHITE, SCRSIZEX // 30,SCRSIZEX * 11 // 20, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, singleButtons))
    return

def storyButtons():
    global currentImageList, currentButtonList
    currentImageList, currentButtonList = [],[] #초기화

    currentButtonList.append(Button( GRAY,"SELECT CHAPTER", BLACK, SCRSIZEX // 20, SCRSIZEX // 4, SCRSIZEY // 10 , SCRSIZEX // 2, SCRSIZEY // 10, lobbyButtons))

    currentImageList.append(Image( "undo", 0, 0, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY,"", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, singleButtons)) #undo 버튼

    currentImageList.append(Image( "stage1", SCRSIZEX // 20, SCRSIZEX // 20, SCRSIZEX // 20, SCRSIZEY // 20))
    currentButtonList.append(Button( GRAY, "", BLACK, 0, 0, 0, SCRSIZEX // 20, SCRSIZEY // 20, lobbyButtons))


    return

def test():
    print("버튼A")
    return



#------------------------여기부터 시작---------------------------------#

storyButtons()

while not done: # loop the game       

    clock.tick(60) #FPS는 60으로

    screen.fill(WHITE) #임시 배경색 (차후에 이미지로 변경될수 있음)

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
                    button.checkFunction()

    #main.runGame(123456)
    #main.runGame(444444)

pygame.quit() # quit pygame