import main
import pygame
import ctypes

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
            
        

        font = pygame.font.SysFont("None", 200) #폰트 설정
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
    currentButtonList.append(Button( BLACK,"MULTI PLAYER", WHITE, SCRSIZEX // 21, SCRSIZEX // 3, SCRSIZEY * 5 // 8 , SCRSIZEX // 3, SCRSIZEY * 3 // 40, test))
    currentButtonList.append(Button( BLACK,"SETTINGS", WHITE, SCRSIZEX // 14, SCRSIZEX // 3, SCRSIZEY *3 // 4, SCRSIZEX // 3, SCRSIZEY * 3 // 40, test))
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
    currentButtonList.append(Button( BLACK,"CUSTOM", WHITE, SCRSIZEX // 30,SCRSIZEX * 11 // 20, SCRSIZEY * 2 // 3, SCRSIZEX // 4, SCRSIZEY // 8, singleButtons))
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

    if main.runGame(f"story/chapter{chapterlevel[0]}/level{chapterlevel[1]}"): #레벨 클리어시
        with open(f"./maps/story/chapter{chapterlevel[0]}/info.dat", "r") as f: #챕터 정보 파일 열기
            lines = f.readlines()
            for line in lines:
                if "cleared=" in line: #클리어된 레벨 목록
                    temp = line.strip("cleared=")
                    clearedList = list(map(lambda x: int(x),temp.split(","))) #문자열의 정수들을 리스트에 저장 
        
        if chapterlevel[1] not in clearedList: #클리어 목록에 레벨이 없다면
            with open(f"./maps/story/chapter{chapterlevel[0]}/info.dat", "a") as f: #챕터 정보 파일 뒤에 이어서 쓰기
                f.write(f",{chapterlevel[1]}")

            
    chapterButtons(chapterlevel[0]) #챕터 선택창 다시 로드하기(CLEARED! 표시를 위해)
    
    return

def undo():
    if currentundo != None: #현재 undo로 지정된 함수 실행
        currentundo()

    return

def test():
    print("test")
    return



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