import tkinter
import pyautogui
import os
import ctypes

brushCheck = True
brushColor = 0
colorTuple = ("black", "red", "green", "blue", "yellow", "cyan", "magenta", "white", "gray") #색 목록
mapX = 0 #맵의 가로 타일 수
mapY = 0 #맵의 세로 타일 수
playerX = 0 #플레이어 시작 X좌표(캔버스 기준)
playerY = 0 #플레이어 시작 Y좌표(캔버스 기준)
tileSize = 50 #타일의 크기
mapOrigin = 300 # 캔버스의 시작 X좌표
mapArray = []

user32 = ctypes.windll.user32
SCRSIZEX = user32.GetSystemMetrics(0)-mapOrigin-50 #화면의 해상도 (픽셀수) 구하기 가로, 왼쪽 여유공간 600, 오른쪽 여유공간 50
SCRSIZEY = user32.GetSystemMetrics(1)-50 #세로, 여유로 50 남김



def sizeChange(): #2차원 배열 크기 변경, 캔버스 생성
    global mapX
    global mapY
    global mapArray
    global canvas
    global tileSize
    global characterCanvas

    if XEntry.get().isdigit() and YEntry.get().isdigit() and int(XEntry.get()) >= 1 and int(XEntry.get()) >= 1 and int(XEntry.get()) <= 150 and int(XEntry.get()) <= 150: #입력값이 정수인지 확인, 1 이상인지 확인
        mapSizeAlert.config(text = XEntry.get() + ", " + YEntry.get())
        canvas.destroy()
        mapX = int(XEntry.get())
        mapY = int(YEntry.get())
        
        tileSize = SCRSIZEY // mapY if SCRSIZEX/mapX > SCRSIZEY/mapY else SCRSIZEX // mapX #타일 크기를 화면비율에 맞추기
        if tileSize > 80: tileSize = 80 # 80 이상은 너무 크므로 100으로 고정

        canvas = tkinter.Canvas(window, width = mapX * tileSize, height = mapY * tileSize)
        mapArray = [[0 for y in range(mapY)] for x in range(mapX)]
       
        drawGrid()
    else:
        mapSizeAlert.config(text = "1 이상 150 이하의 정수 입력")

def drawGrid(): #격자 그리기
    global canvas
    for x in range(mapX):
        for y in range(mapY):
            canvas.create_rectangle(tileSize * x, tileSize * y, tileSize * (x + 1), tileSize * (y + 1), fill = "black")

    for x in range(mapX): canvas.create_line(tileSize * x, 0, tileSize * x, tileSize * (y + 1), fill = "gray") # 세로줄긋기
    for y in range(mapY): canvas.create_line(0, tileSize * y, tileSize * (x + 1), tileSize * y, fill = "gray") # 가로줄긋기

    canvas.bind("<Button-1>", colorChange) #클릭 / 드래그 감지
    canvas.bind("<B1-Motion>", colorChange) 

    canvas.place(x = mapOrigin, y = 0)

def colorChange(event): #색 변경
    global canvas
    global mapArray
    x = (pyautogui.position()[0] - mapOrigin) // tileSize 
    y = (pyautogui.position()[1]) // tileSize
    if x < mapX and y < mapY:
        if brushCheck: #타일 색을 선택했을 경우
            mapArray[x][y] = brushColor
            canvas.create_rectangle(x * tileSize + 1, y * tileSize + 1, x * tileSize + tileSize - 1, y * tileSize + tileSize - 1, fill = colorTuple[brushColor]) # 1씩 작게 채움으로써 grid를 남긴다
        else: #스위치 색을 선택했을 경우
            mapArray[x][y] = colorTuple[brushColor][0]
            canvas.create_rectangle(x * tileSize + 1, y * tileSize + 1, x * tileSize + tileSize - 1, y * tileSize + tileSize - 1, fill = "black")
            canvas.create_rectangle((x + 1 / 4) * tileSize, (y + 1 / 4) * tileSize, (x + 3 / 4) * tileSize, (y + 3 / 4) * tileSize, fill = colorTuple[brushColor])

def setBrushColor(color): #타일 버튼 클릭 시
    global brushColor, brushCheck
    brushCheck = True
    brushColor = color
    
def setSwitchColor(color): #스위치 버튼 클릭 시
    global brushColor, brushCheck
    brushCheck = False
    brushColor = color

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
        f.close
        return True
    except: # 오류 발생시 실패를 알린다
        print("저장 실패")
        return False
    
def playerPos(event): #플레이어 시작 좌표
    global playerX
    global playerY
    if pyautogui.position()[0] >= mapOrigin and pyautogui.position()[0] <= tileSize * mapX + mapOrigin and pyautogui.position()[1] >= 0 and pyautogui.position()[1] <= tileSize * mapY:
        playerX = round((pyautogui.position()[0] - mapOrigin) / tileSize, 1)
        playerY = round(pyautogui.position()[1] / tileSize, 1)
        positionLabel.config(text = f"{playerX},{playerY}")
    character()

def isNumeric(s): #문자열 실수 판단
    try:
        float(s)
        return True
    except ValueError:
        return False
 
def character(): #플레이어 캐릭터 생성
    global characterCanvas
    global playerX
    global playerY

    if isNumeric(playerWidth.get()) and isNumeric(playerHeight.get()): #플레이어 키와 너비가 실수인지 확인
        
        if playerX - float(playerWidth.get()) / 2 <= 0:
            playerX = float(playerWidth.get()) / 2 + 0.1

        elif playerX + float(playerWidth.get()) / 2 >= int(XEntry.get()):
            playerX = int(XEntry.get()) - float(playerWidth.get()) / 2 - 0.1
        
        if playerY - float(playerHeight.get()) / 2 <= 0:
            playerY = float(playerHeight.get()) / 2 + 0.1
        elif playerY + float(playerHeight.get()) / 2 >= int(YEntry.get()):
            playerY = int(YEntry.get()) - float(playerHeight.get()) / 2 - 0.1
        
        mouseX = (playerX - float(playerWidth.get()) / 2) * tileSize + mapOrigin #마우스로 클릭한 지점이 맵에서 X 좌표인지(타일기준)
        mouseY = (playerY - float(playerHeight.get()) / 2) * tileSize #Y
    
        characterCanvas.destroy()
        characterCanvas = tkinter.Canvas(width = float(playerWidth.get()) * tileSize, height = float(playerHeight.get()) * tileSize)
        characterCanvas.create_rectangle(0, 0, float(playerWidth.get()) * tileSize, float(playerHeight.get()) * tileSize, fill = "olive")
        characterCanvas.place(x = mouseX , y = mouseY) 


# ------------------------ GUI 요소 생성 ------------------------

window = tkinter.Tk()
window.title("맵에디터") #창의 이름

window.resizable(False, False) #창 크기 조절 가능 여부
window.attributes("-fullscreen", True) #전체화면
window.bind("<Button-3>", playerPos)

#레이블 생성
mapSizeAlert = tkinter.Label(window, text = "")
XLabel = tkinter.Label(window, text = "맵의 가로 길이 입력")
YLabel = tkinter.Label(window, text = "맵의 세로 길이 입력")
positionLabel = tkinter.Label(window, text = "")
playerWidthLabel = tkinter.Label(window, text = "플레이어 너비 입력")
playerHeigheLabel = tkinter.Label(window, text = "플레이어 키 입력")
jumpHeightLabel = tkinter.Label(window, text = "점프 높이 입력")
jumpTimeLabel = tkinter.Label(window, text = "점프 시간 입력")
mapNameAlert = tkinter.Label(window, text = "저장할 이름 입력")
speedLabel = tkinter.Label(window, text = "이동 속도 입력")
backgroundLabel = tkinter.Label(window, text = "배경사진 이름 입력")

#엔트리 생성
XEntry = tkinter.Entry(window)
YEntry = tkinter.Entry(window)
jumpHeight = tkinter.Entry(window)
jumpTime = tkinter.Entry(window)
mapName = tkinter.Entry(window)
speed = tkinter.Entry(window)
playerWidth = tkinter.Entry(window)
playerHeight = tkinter.Entry(window)
background = tkinter.Entry(window)

#버튼 생성
mapButton = tkinter.Button(window, text = "맵 생성", command = sizeChange)
saveButton = tkinter.Button(window, text = "맵 저장", command = save)

colorButton = []
for i in range(9):
    colorButton.append(tkinter.Button(window, command = lambda i=i: setBrushColor(i), bg = colorTuple[i], width = 5)) #i=i로 i를 반복문의 현재 값으로 바꿈

switchButton = []
for i in range(7):
    switchButton.append(tkinter.Button(window, command = lambda i=i: setSwitchColor(i+1), bg = colorTuple[i+1], width = 5, text = "스위치"))
 
#캔버스 생성
canvas = tkinter.Canvas()
characterCanvas = tkinter.Canvas()


# ------------------------ GUI 배치 ------------------------

mapSizeAlert.grid()
XLabel.grid()
XEntry.grid()
YLabel.grid()
YEntry.grid()
mapButton.grid()

for button in colorButton:
    button.grid()

for button in switchButton:
    button.grid()

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
window.mainloop()