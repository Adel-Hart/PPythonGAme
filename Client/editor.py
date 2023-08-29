import tkinter as tk
import pyautogui
import os
import ctypes
from math import trunc
import re

import socket




with open("../server/serverip.txt","r") as f:
    HOST = f.readline()
PORT = 8080

'''
이재용 작성
사용 모듈 : 
'''

brushColor = 0
brushCheck = True
colorList = ("black", "red", "green", "blue", "yellow", "cyan", "magenta", "white", "gray") #색 목록
mapOrigin = 300 # 캔버스의 시작 X좌표
mapArray = []

user32 = ctypes.windll.user32
SCRSIZEX = user32.GetSystemMetrics(0)-mapOrigin-50 #화면의 해상도 (픽셀수) 구하기 가로, 왼쪽 여유공간 600, 오른쪽 여유공간 50
SCRSIZEY = user32.GetSystemMetrics(1)-50 #세로, 여유로 50 남김

def drawMap(): #맵 생성

    global mapX, mapY, mapArray, canvas, tileSize, playerX, playerY, goalX, goalY, PWidth, PHeight

    if XEntry.get().isdigit() and YEntry.get().isdigit() and 1 <= int(XEntry.get()) <= 150 and 1 <= int(YEntry.get()) <= 150: #입력값이 정수인지 확인, 1 이상 150 이하인지 확인

        canvas.destroy() #맵, 플레이어, 도착지점 제거
        playerCanvas.destroy()
        goalCanvas.destroy()

        playerX = None #변수 초기화
        playerY = None
        goalX = None
        goalY = None
        PWidth = None
        PHeight = None

        mapX = int(XEntry.get()) #맵의 가로 타일 수
        mapY = int(YEntry.get()) #맵의 세로 타일 수
        
        #타일 사이즈 지정
        tileSize = SCRSIZEY // mapY if SCRSIZEX/mapX > SCRSIZEY/mapY else SCRSIZEX // mapX #타일 크기를 화면비율에 맞추기
        if tileSize > 80: tileSize = 80 # 80 이상은 너무 크므로 100으로 고정

        canvas = tk.Canvas(window, width = mapX * tileSize, height = mapY * tileSize)
        mapArray = [[0 for y in range(mapY)] for x in range(mapX)]

        for i in range(mapX):
            for j in range(mapY):
                canvas.create_rectangle(tileSize * i, tileSize * j, tileSize * (i+1), tileSize * (j+1), fill = "black")

        for i in range(mapX): canvas.create_line(tileSize * i, 0, tileSize * i, tileSize * (j+1), fill = "gray") # 세로줄긋기
        for j in range(mapY): canvas.create_line(0, tileSize * j, tileSize * (i+1), tileSize * j, fill = "gray") # 가로줄긋기

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
            canvas.create_rectangle(tileX + 1, tileY + 1, tileX + tileSize - 1, tileY + tileSize - 1, fill = colorList[brushColor]) # 1씩 작게 채움으로써 grid를 남긴다
        
        else: #스위치 버튼을 클릭 경우
            mapArray[x][y] = colorList[brushColor][0]
            canvas.create_rectangle(tileX + 1, tileY + 1, tileX + tileSize - 1, tileY + tileSize - 1, fill = "black") #타일을 검정색으로 초기화
            canvas.create_rectangle(tileX + tileSize/4, tileY + tileSize/4, tileX + tileSize*3/4, tileY + tileSize*3/4, fill = colorList[brushColor])
    
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

def save(fileName): #맵 파일 작성
    if valueCheck():
        try: # 오류 대비
            #temp 폴더는 save될때 마다 만들면 오류 나니까, 너가 먼저 만들고, 저장만 하게 하면 됨 - 김동훈 남김
            f = open(fileName+mapName.get()+"/map.dat","w") #맵이름 폴더 안에 dat 파일 생성
            for y in range(mapY):
                for x in range(mapX):
                    f.write(str(mapArray[x][y]))
                f.write("\n") 
            f.write("!" + f"{playerX},{playerY}")
            f.write("\n@" + f"{PWidth},{PHeight}")
            f.write("\n#" + jump(float(jumpHeight.get()), float(jumpTime.get())) + speed.get())
            f.write("\n$" + background.get())
            f.write("\n%" + f"{goalX},{goalY}")
            f.close
            return True
        except: # 오류 발생시 실패를 알린다
            print("저장 실패")
            return False
    
def player(event): #플레이어 생성

    global playerCanvas, playerX, playerY, PWidth, PHeight

    if isMap():

        playerX = round((pyautogui.position()[0] - mapOrigin) / tileSize, 1)
        playerY = round(pyautogui.position()[1] / tileSize, 1)

        if isNumeric(playerWidth.get()) and isNumeric(playerHeight.get()) and float(playerWidth.get()) < mapX and float(playerHeight.get()) < mapY: #플레이어 키와 너비가 실수인지, 맵보다 작은지 확인
            
            PWidth = float(playerWidth.get()) #플레이어 폭
            PHeight = float(playerHeight.get()) #플레이어 높이

            #플레이어가 맵 밖에 있을 경우 맵 안으로 자동조정

            halfPWidth = PWidth/2 #플레이어 폭의 절반
            halfPHeight = PHeight/2 #플레이어 높이의 절반

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
            playerCanvas = tk.Canvas(width = PWidth * tileSize, height = PHeight * tileSize)
            playerCanvas.create_rectangle(0, 0, PWidth * tileSize, PHeight * tileSize, fill = "olive")
            playerCanvas.place(x = mouseX , y = mouseY) 
            
            return
        
def isNumeric(s): #문자열 실수 판단
    try:
        if float(s) != 0:
            return True
        else:
            return False
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
        if goalX - 0.5 <= 0: #도착지점 좌측이 맵 밖일 경우
            goalX = 0.5
        elif goalX + 0.5 >= mapX: #도착지점 우측이 맵 밖일 경우
            goalX = mapX - 0.5
        else: #도착지점 좌표 0.5 기준으로 조정
            if goalX - trunc(goalX) <= 0.25:
                goalX = trunc(goalX)
            elif 0.25 < goalX - trunc(goalX) <= 0.75:
                goalX = trunc(goalX) + 0.5
            elif 0.75 < goalX - trunc(goalX):
                goalX = trunc(goalX) + 1

        #도착지점 Y값 조정
        if goalY - 1 <= 0: #도착지점 하단이 맵 밖일 경우
            goalY = 1
        elif goalY + 1 >= mapY: #도착지점 하단이 맵 밖일 경우
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

def valueCheck(): #모든 값이 정상적으로 채워져있는지 검사

    check = re.compile("[^a-zA-Z0-9]") #영어와 숫자가 아닌 값들을 검사
    
    try:
        valueList = [mapX, isNumeric(jumpHeight.get()), isNumeric(jumpTime.get()), isNumeric(speed.get()), PWidth, background.get(), goalX] #검사할 값 목록

        if all(valueList) and not check.search(mapName.get()): # valueList의 값이 모두 참이고, 맵 이름에 영어와 숫자를 제외한 문자가 없다면
            return True
        else:
            return False
        
    except: #값이 정의되지 않았을 때(예 : 맵 생성 버튼을 누르지 않음)
        return False

def runEditor():





    global window, XEntry, YEntry, jumpHeight, jumpTime, mapName, speed, playerWidth, playerHeight, background, canvas, playerCanvas, goalCanvas
    
    buttonX = SCRSIZEX / 35 #버튼 사이의 X축 간격
    buttonY = SCRSIZEY / 30 #버튼 사이의 Y축 간격


    # ------------------------ GUI 요소 생성 ------------------------

    window = tk.Tk()
    window.title("맵에디터") #창의 이름

    window.resizable(False, False) #창 크기 조절 가능 여부
    window.attributes("-fullscreen", True) #전체화면
    window.bind("<Button-3>", player) #좌클릭 감지
    window.bind("<Button-2>", goal) #휠클릭 감지

    #레이블 생성
    XLabel = tk.Label(window, text = "맵의 가로 길이 입력")
    YLabel = tk.Label(window, text = "맵의 세로 길이 입력")
    playerWidthLabel = tk.Label(window, text = "플레이어 너비 입력")
    playerHeigheLabel = tk.Label(window, text = "플레이어 키 입력")
    jumpHeightLabel = tk.Label(window, text = "점프 높이 입력")
    jumpTimeLabel = tk.Label(window, text = "점프 시간 입력")
    mapNameLabel = tk.Label(window, text = "저장할 이름 입력")
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
    saveButton = tk.Button(window, text = "맵 저장", command = lambda: save("./maps/"))
    closeButton = tk.Button(window, text = "에디터 종료", command = close)
    mapUpload = tk.Button(window, text = "맵업로드", command = lambda: save("./temp/"))

    colorButton = []
    for i in range(9):
        colorButton.append(tk.Button(window, command = lambda i=i: setBrushColor(i), bg = colorList[i], width = 5))

    switchButton = []
    for i in range(7):
        switchButton.append(tk.Button(window, command = lambda i=i: setSwitchColor(i+1), bg = colorList[i+1], width = 5, text = "스위치"))
    
    #캔버스 생성
    canvas = tk.Canvas()
    playerCanvas = tk.Canvas()
    goalCanvas = tk.Canvas()

    # ------------------------ GUI 배치 ------------------------

    guiLayout = [XLabel, XEntry, YLabel, YEntry, mapButton,
                playerHeigheLabel, playerHeight, playerWidthLabel, playerWidth, 
                jumpHeightLabel, jumpHeight, jumpTimeLabel, jumpTime, speedLabel, speed,
                mapNameLabel, mapName, backgroundLabel, background, saveButton, closeButton, mapUpload]

    for i in range(len(guiLayout)):
        guiLayout[i].grid(row=i)


    for i in range(9):
        colorButton[i].grid(row = len(guiLayout)+i+1, column = 0)

    for i in range(7):
        switchButton[i].grid(row = len(guiLayout)+i+2, column = 1)


    window.mainloop()

    return


class tcpSock():
    def __init__(self):
        pass

    def run(self):
        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP소켓 생성
        print("연결 시작")
        self.tcpSock.connect((HOST, PORT))
        print("연결성공")
    
    def sendMapfile(self, mapCode: str):
        if f"{mapCode}.dat" in os.listdir("./temp/"): #보낼 파일이 존재하지 않으면, 안되게 False전송

            self.sock.send(f"2000CODE{mapCode}") #맵코드 확인 요청, 정보 : socket의 send함수는 보낸 바이트 수를 반환 합니다.
            data = self.sock.recv(1024)
            if data == "0080":
                with open(mapCode, 'rb') as f:
                    try:
                        data = f.read(1024) #파일에서 1024바이트 씩 읽기
                        while data: #data가 0 (다 읽을 때 까지), 이렇게 하는 이유는 1024바이트 씩 읽고, 없어질때를 더 효과적으로 표현 가능
                            #만약 while이 없었으면 f.read(1024)를 for문으로 돌려야 했다.
                            self.sock.send(data.encode()) #1024 크기의 데이터를 보낸다, 참고 - 소켓의 send함수는 리턴이 보낸 데이터의 크기
                            data = f.read(1024) #다시 1024만큼 읽어본다.

                        self.sock.send("0080".encode()) #성공시 0080프로토콜 전송
                        return "COMPLETE" #True 출력
                         
                    except Exception as ex:
                        print(f"전송 중 오류 : {ex}")
                        self.sock.send("0000".encode()) #오류 시 0000프로토콜
                        return "SOMETHING ERROR" #오류메세지와 true출력

                        
                            

            elif data == "0000":
                return "ALREADYEXIST" #실패시 NAMEFAIL, 클라이언트 측에선 이 함수를 실행할때 변수 안에 넣고, NAMEFAIL시 네임 다시 짓게하면 됨
            else:
                pass
        
        else:
            print("파일이 없습니다")
            return "NOFILE"
