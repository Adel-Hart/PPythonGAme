import tkinter as tk
import pyautogui
import os
import ctypes
from math import trunc
import keyboard




'''
이재용 작성
사용 모듈 : 
'''


brushCheck = True #True일시 타일, False일시 스위치
brushColor = 0
colorTuple = ("black", "red", "green", "blue", "yellow", "cyan", "magenta", "white", "gray") #색 목록
playerX = 0 #플레이어 시작 X좌표
playerY = 0 #플레이어 시작 Y좌표
goalX = 0
goalY = 0
tileSize = 50 #타일의 크기
mapOrigin = 300 # 캔버스의 시작 X좌표
mapArray = []

user32 = ctypes.windll.user32
SCRSIZEX = user32.GetSystemMetrics(0)-mapOrigin-50 #화면의 해상도 (픽셀수) 구하기 가로, 왼쪽 여유공간 600, 오른쪽 여유공간 50
SCRSIZEY = user32.GetSystemMetrics(1)-50 #세로, 여유로 50 남김

def drawMap(): #맵 생성

    global mapX, mapY, mapArray, canvas, tileSize, playerX, playerY, goalX, goalY

    if XEntry.get().isdigit() and YEntry.get().isdigit() and 1 <= int(XEntry.get()) <= 150 and 1 <= int(YEntry.get()) <= 150: #입력값이 정수인지 확인, 1 이상 150 이하인지 확인

        canvas.destroy() #맵, 플레이어, 도착지점 제거
        playerCanvas.destroy()
        goalCanvas.destroy()

        playerX = 0 #플레이어, 도착지점 좌표 초기화
        playerY = 0
        goalX = 0
        goalY = 0 

        mapX = int(XEntry.get()) #맵의 가로 타일 수
        mapY = int(YEntry.get()) #맵의 세로 타일 수
        
        tileSize = SCRSIZEY // mapY if SCRSIZEX/mapX > SCRSIZEY/mapY else SCRSIZEX // mapX #타일 크기를 화면비율에 맞추기
        if tileSize > 80: tileSize = 80 # 80 이상은 너무 크므로 100으로 고정

        canvas = tk.Canvas(window, width = mapX * tileSize, height = mapY * tileSize)
        mapArray = [[0 for y in range(mapY)] for x in range(mapX)]

        for i in range(mapX):
            for j in range(mapY):
                canvas.create_rectangle(tileSize * i, tileSize * j, tileSize * (i + 1), tileSize * (j + 1), fill = "black")

        for i in range(mapX): canvas.create_line(tileSize * i, 0, tileSize * i, tileSize * (j + 1), fill = "gray") # 세로줄긋기
        for j in range(mapY): canvas.create_line(0, tileSize * j, tileSize * (i + 1), tileSize * j, fill = "gray") # 가로줄긋기

        canvas.bind("<Button-1>", colorChange) #클릭 / 드래그 감지
        canvas.bind("<B1-Motion>", colorChange) 

        canvas.place(x = mapOrigin, y = 0)
    return

def isMap(): #클릭 좌표가 맵 안인지 판단
    
    global x, y

    x = (pyautogui.position()[0] - mapOrigin) // tileSize #마우스의 타일 X좌표
    y = (pyautogui.position()[1]) // tileSize #마우스의 타일 Y좌표

    if x < mapX and y < mapY:
        return True
    else:
        return False



def colorChange(event): #색 변경

    global canvas, mapArray

    if isMap():

        tileX = x * tileSize #클릭 타일의 좌상단 X좌표
        tileY = y * tileSize #클릭 타일의 좌상단 Y좌표

        if brushCheck: #타일 버튼을 클릭한 경우
            mapArray[x][y] = brushColor
            canvas.create_rectangle(tileX + 1, tileY + 1, tileX + tileSize - 1, tileY + tileSize - 1, fill = colorTuple[brushColor]) # 1씩 작게 채움으로써 grid를 남긴다
        
        else: #스위치 버튼을 클릭 경우
            mapArray[x][y] = colorTuple[brushColor][0]
            canvas.create_rectangle(tileX + 1, tileY + 1, tileX + tileSize - 1, tileY + tileSize - 1, fill = "black") #타일을 검정색으로 초기화
            canvas.create_rectangle(tileX + tileSize/4, tileY + tileSize/4, tileX + tileSize*3/4, tileY + tileSize*3/4, fill = colorTuple[brushColor])
    
    return

def setBrushColor(color): #타일 버튼 클릭 시
    global brushColor, brushCheck
    brushCheck = True
    brushColor = color
    return
    
def setSwitchColor(color): #스위치 버튼 클릭 시
    global brushColor, brushCheck
    brushCheck = False
    brushColor = color
    return

def jump(height,time): #점프속도와 중력가속도 계산
    v = height * 4 / time
    g = height * 8 / (time * time)
    return f"{v},{g},"

def save(): #맵 파일 작성
    try: # 오류 대비
        os.makedirs("./maps/"+mapName.get(), exist_ok=True) # maps/맵이름 폴더 만들기
        f = open("./maps/"+mapName.get()+"/map.dat","w") #맵이름 폴더 안에 dat 파일 생성
        for y in range(mapY):
            for x in range(mapX):
                f.write(str(mapArray[x][y]))
            f.write("\n") 
        f.write("!" + f"{playerX},{playerY}")
        f.write("\n@" + playerWidth.get() + "," + playerHeight.get())
        f.write("\n#" + jump(float(jumpHeight.get()), float(jumpTime.get())) + speed.get())
        f.write("\n$" + background.get())
        f.write("\n%" + f"{goalX},{goalY}")
        f.close
        return True
    except: # 오류 발생시 실패를 알린다
        print("저장 실패")
        return False
    
def player(event): #플레이어 생성

    global playerCanvas, playerX, playerY

    if isMap():

        playerX = round((pyautogui.position()[0] - mapOrigin) / tileSize, 1)
        playerY = round(pyautogui.position()[1] / tileSize, 1)
        positionLabel.config(text = f"{playerX},{playerY}")

        if isNumeric(playerWidth.get()) and isNumeric(playerHeight.get()): #플레이어 키와 너비가 실수인지 확인
            
            halfPWidth = float(playerWidth.get()) / 2 #플레이어 폭의 절반
            halfPHeight = float(playerHeight.get()) / 2 #플레이어 높이의 절반

            #플레이어가 맵 밖에 있을 경우 맵 안으로 자동조정

            if playerX - halfPWidth <= 0: #플레이어 좌측이 맵 밖일 경우
                playerX = halfPWidth + 0.1
            elif playerX + halfPWidth >= mapX: #플레이어 우측이 맵 밖일 경우
                playerX = mapX - halfPWidth - 0.1
            
            if playerY - halfPHeight <= 0: #플레이어 하단이 맵 밖일 경우
                playerY = halfPHeight + 0.1
            elif playerY + halfPHeight >= mapY: #플레이어 상단이 맵 밖일 경우
                playerY = mapY - halfPHeight - 0.1
            
            mouseX = (playerX - halfPWidth) * tileSize + mapOrigin #마우스로 클릭한 지점이 맵에서 X 좌표인지(타일기준)
            mouseY = (playerY - halfPHeight) * tileSize #Y
        
            playerCanvas.destroy()
            playerCanvas = tk.Canvas(width = float(playerWidth.get()) * tileSize, height = float(playerHeight.get()) * tileSize)
            playerCanvas.create_rectangle(0, 0, float(playerWidth.get()) * tileSize, float(playerHeight.get()) * tileSize, fill = "olive")
            playerCanvas.place(x = mouseX , y = mouseY) 
            
            return
        
def isNumeric(s): #문자열 실수 판단
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def close(): #종료 함수
    window.destroy() #창 닫기

 
def goal(evnet): #도착지점 생성 (넓이 1*2)

    global goalCanvas, goalX, goalY

    if isMap(): #클릭 좌표가 맵 안인지
        goalX = round((pyautogui.position()[0] - mapOrigin) / tileSize, 2)
        goalY = round(pyautogui.position()[1] / tileSize, 2)

        #도착지점 X값 조정
        if goalX - 0.5 <= 0: #도착지점이 맵을 넘어가는 경우
            goalX = 0.5
        elif goalX + 0.5 >= mapX:
            goalX = mapX - 0.5
        else: #도착지점 좌표 0.5 기준으로 조정
            if goalX - trunc(goalX) <= 0.25:
                goalX = trunc(goalX)
            elif 0.25 < goalX - trunc(goalX) <= 0.75:
                goalX = trunc(goalX) + 0.5
            elif 0.75 < goalX - trunc(goalX):
                goalX = trunc(goalX) + 1
        #도착지점 Y값 조정
        if goalY - 1 <= 0: #도착지점이 맵을 넘어가는 경우
            goalY = 1
        elif goalY + 1 >= mapY :
            goalY = mapY - 1
        else: #도착지점 좌표 0.5 기준으로 조정
            if goalY - trunc(goalY) <= 0.25: 
                goalY = trunc(goalY)
            elif 0.25 < goalY - trunc(goalY) <= 0.75:
                goalY = trunc(goalY) + 0.5
            elif 0.75 < goalY - trunc(goalY):
                goalY = trunc(goalY) + 1

        goalCanvas.destroy()
        goalCanvas = tk.Canvas(width = tileSize, height = 2 * tileSize)
        goalCanvas.create_rectangle(0, 0,  tileSize, 2 * tileSize, fill = "purple")
        goalCanvas.place(x = (goalX - 0.5) * tileSize + mapOrigin , y = (goalY - 1) * tileSize) 

        return



def runEditor():

    global window, XEntry, YEntry, jumpHeight, jumpTime, mapName, speed, playerWidth, playerHeight, background, positionLabel, canvas, playerCanvas, goalCanvas

    buttonX = SCRSIZEX / 35 #버튼 사이의 X축 간격
    buttonY = SCRSIZEY / 30 #버튼 사이의 Y축 간격
    

    # ------------------------ GUI 요소 생성 ------------------------

    window = tk.Tk()
    window.title("맵에디터") #창의 이름

    window.resizable(False, False) #창 크기 조절 가능 여부
    window.attributes("-fullscreen", True) #전체화면
    window.bind("<Button-3>", player) #좌클릭 감지 -> player함수 실행
    window.bind("<Button-2>", goal) #휠클릭 감지 -> goal함수 실행

    #레이블 생성
    XLabel = tk.Label(window, text = "맵의 가로 길이 입력")
    YLabel = tk.Label(window, text = "맵의 세로 길이 입력")
    positionLabel = tk.Label(window, text = "")
    playerWidthLabel = tk.Label(window, text = "플레이어 너비 입력")
    playerHeigheLabel = tk.Label(window, text = "플레이어 키 입력")
    jumpHeightLabel = tk.Label(window, text = "점프 높이 입력")
    jumpTimeLabel = tk.Label(window, text = "점프 시간 입력")
    mapNameAlert = tk.Label(window, text = "저장할 이름 입력")
    speedLabel = tk.Label(window, text = "이동 속도 입력")
    backgroundLabel = tk.Label(window, text = "배경사진 이름 입력")

    #엔트리 생성
    XEntry = tk.Entry(window)
    YEntry = tk.Entry(window)
    jumpHeight = tk.Entry(window)
    jumpTime = tk.Entry(window)
    mapName = tk.Entry(window)
    speed = tk.Entry(window)
    playerWidth = tk.Entry(window)
    playerHeight = tk.Entry(window)
    background = tk.Entry(window)

    #버튼 생성
    mapButton = tk.Button(window, text = "맵 생성", command = drawMap)
    saveButton = tk.Button(window, text = "맵 저장", command = save)
    closeButton = tk.Button(window, text = "종료", command = close)

    colorButton = []
    for i in range(9):
        colorButton.append(tk.Button(window, command = lambda i=i: setBrushColor(i), bg = colorTuple[i], width = 5))

    switchButton = []
    for i in range(7):
        switchButton.append(tk.Button(window, command = lambda i=i: setSwitchColor(i+1), bg = colorTuple[i+1], width = 5, text = "스위치"))
    
    #캔버스 생성
    canvas = tk.Canvas()
    playerCanvas = tk.Canvas()
    goalCanvas = tk.Canvas()


    # ------------------------ GUI 배치 ------------------------

    XLabel.grid()
    XEntry.grid()
    YLabel.grid()
    YEntry.grid()
    mapButton.grid()

    for i in range(9):
        colorButton[8-i].place(x = buttonX, y = SCRSIZEY - buttonY * (i+2))

    for i in range(7):
        switchButton[6-i].place(x = buttonX * 2, y = SCRSIZEY - buttonY * (i+3))

    positionLabel.grid()
    playerHeigheLabel.grid()
    playerHeight.grid()
    playerWidthLabel.grid()
    playerWidth.grid()
    jumpHeightLabel.grid()
    jumpHeight.grid()
    jumpTimeLabel.grid()
    jumpTime.grid()
    speedLabel.grid()
    speed.grid()
    mapNameAlert.grid()
    mapName.grid()
    backgroundLabel.grid()
    background.grid()
    saveButton.grid()
    closeButton.grid()
    window.mainloop()

    return