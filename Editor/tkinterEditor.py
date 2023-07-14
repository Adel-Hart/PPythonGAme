import tkinter
import pyautogui
import os

brushColor = 0 
colorTuple = ("black", "red", "green", "blue", "yellow", "cyan", "magenta", "white", "gray") 
mapX = 0
mapY = 0
gridSize = 50 #격자 한칸의 크기
mapArray = []

def sizeChange(): #2차원 배열 크기 변경, 캔버스 생성
    global mapX
    global mapY
    global mapArray
    global canvas
    if XEntry.get().isdigit() and YEntry.get().isdigit(): #입력값이 정수인지 확인
        mapSizeAlert.config(text = XEntry.get() + ", " + YEntry.get())
        canvas.destroy()
        mapX = int(XEntry.get())
        mapY = int(YEntry.get())
        canvas = tkinter.Canvas(window, width = mapX * gridSize, height = mapY * gridSize)
        mapArray = [[0 for y in range(mapY)] for x in range(mapX)]
        drawGrid()
    else:
        mapSizeAlert.config(text = "정수를 입력해주세요...!")

def drawGrid(): #격자 그리기
    global canvas
    for x in range(mapX):
        for y in range(mapY):
            canvas.create_rectangle(gridSize * x, gridSize * y, gridSize * (x + 1), gridSize * (y + 1), fill = "black")
    canvas.bind("<Button-1>", colorChange)
    canvas.bind("<B1-Motion>", colorChange)
    canvas.place(x = 600, y = 0)

def colorChange(event): #색 변경
    global canvas
    global mapArray
    x = (pyautogui.position()[0]-600) // gridSize 
    y = (pyautogui.position()[1]) // gridSize
    if x < mapX and y < mapY:
        mapArray[x][y] = brushColor
        canvas.create_rectangle(x * gridSize, y * gridSize, x * gridSize + gridSize, y * gridSize + gridSize, fill = colorTuple[brushColor])

def setBrushColor(color):
    global brushColor
    brushColor = color

def jump(height,time): #점프속도와 중력가속도 계산
    v = height * 4 / time
    g = height * 8 / (time * time)
    return f"{v},{g},"

def save(): #맵 파일 작성
    f = open("map.dat","w")
    for y in range(mapY):
        for x in range(mapX):
            f.write(str(mapArray[x][y]))
        f.write("\n") 
    f.write("!" + position.get())
    f.write("\n@" + size.get())
    f.write("\n#" + jump(float(jumpHeight.get()), float(jumpTime.get())) + speed.get())

# ------------------------ GUI 요소 생성 ------------------------

window = tkinter.Tk()
window.title("맵에디터") #창의 이름
window.geometry("1200x800+100+100") #창의 너비, 높이
window.resizable(False, False) #창 크기 조절 가능 여부
window.attributes("-fullscreen", True) #전체화면

#레이블 생성
mapSizeAlert = tkinter.Label(window, text = "")
XLabel = tkinter.Label(window, text = "맵의 가로 길이 입력")
YLabel = tkinter.Label(window, text = "맵의 세로 길이 입력")
positionLabel = tkinter.Label(window, text = "시작 좌표 입력 \nx,y의 형식으로")
sizeLabel = tkinter.Label(window, text = "플레이어 크기 입력 \nx,y의 형식으로")
jumpHeightLabel = tkinter.Label(window, text = "점프 높이 입력")
jumpTimeLabel = tkinter.Label(window, text = "점프 시간 입력")
mapNameAlert = tkinter.Label(window, text = "저장할 이름 입력")
speedLabel = tkinter.Label(window, text = "이동 속도 입력")

#엔트리 생성
XEntry = tkinter.Entry(window)
YEntry = tkinter.Entry(window)
jumpHeight = tkinter.Entry(window)
jumpTime = tkinter.Entry(window)
mapName = tkinter.Entry(window)
speed = tkinter.Entry(window)
position = tkinter.Entry(window)
size = tkinter.Entry(window)

#버튼 생성
button = tkinter.Button(window, text = "확인", command = sizeChange)
saveButton = tkinter.Button(window, text = "저장", command = save)

#색 변경 버튼 생성
colorButton = []
for i in range(9):
    colorButton.append(tkinter.Button(window, command = lambda i=i: setBrushColor(i), bg = colorTuple[i], width = 5)) #i=i로 i를 람다의 지역 변수로 가져옴

#캔버스 생성
canvas = tkinter.Canvas()

# ------------------------ GUI 배치 ------------------------

mapSizeAlert.grid()
XLabel.grid()
XEntry.grid()
YLabel.grid()
YEntry.grid()
button.grid()

for button in colorButton:
    button.grid()

positionLabel.grid()
position.grid()
sizeLabel.grid()
size.grid()
jumpHeightLabel.grid()
jumpHeight.grid()
jumpTimeLabel.grid()
jumpTime.grid()
speedLabel.grid()
speed.grid()
mapNameAlert.grid()
mapName.grid()
saveButton.grid()
window.mainloop()