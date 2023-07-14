import tkinter
import pyautogui

window = tkinter.Tk()
window.title("맵에디터") #창의 이름
window.geometry("1200x800+100+100") #창의 너비, 높이
window.resizable(False, False) #창 크기 조절 가능 여부
window.attributes("-fullscreen", True) #전체화면

inputFrame = tkinter.Frame(window)
inputFrame.place(x = 0, y = 0)
gridFrame = tkinter.Frame(window, relief="solid", bd=2)
gridFrame.place(x = 600, y = 0)
brushColor = 3
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
    if XEntry.get().isdigit() and YEntry.get().isdigit(): 
        mapSizeAlert.config(text = XEntry.get() + ", " + YEntry.get())
        canvas.destroy()
        mapX = int(XEntry.get())
        mapY = int(YEntry.get())
        canvas = tkinter.Canvas(gridFrame, width = mapX * gridSize, height = mapY * gridSize)
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
    canvas.grid()

def colorChange(event): #색 변경
    global canvas
    global mapArray
    x = (pyautogui.position()[0]-600) // gridSize 
    y = (pyautogui.position()[1]) // gridSize
    if x < mapX and y < mapY:
        mapArray[x][y] = brushColor
        canvas.create_rectangle(x * gridSize, y * gridSize, x * gridSize + gridSize, y * gridSize + gridSize, fill = colorTuple[brushColor])

def blackBrush():
    global brushColor
    brushColor = 0
def redBrush():
    global brushColor
    brushColor = 1
def greenBrush():
    global brushColor
    brushColor = 2
def blueBrush():
    global brushColor
    brushColor = 3
def yellowBrush():
    global brushColor
    brushColor = 4
def cyanBrush():
    global brushColor
    brushColor = 5
def magentaBrush():
    global brushColor
    brushColor = 6
def whiteBrush():
    global brushColor
    brushColor = 7
def grayBrush():
    global brushColor
    brushColor = 8

# def debug():
#     print(mapArray)

# def click(event): 
#     print(pyautogui.position())

def jump(height,time):
    int
    v = height * 4 / time
    g = height * 8 / (time * time)
    return f"{v},{g},"

def save():
    f = open(mapName.get()+".dat","w")
    for y in range(mapY):
        for x in range(mapX):
            f.write(str(mapArray[x][y]))
        f.write("\n") 
    f.write("!" + position.get())
    f.write("\n@" + size.get())
    f.write("\n#" + jump(float(jumpHeight.get()), float(jumpTime.get())) + speed.get())

# window.bind("<Button-1>", click)
mapSizeAlert = tkinter.Label(inputFrame, text = "")
XLabel = tkinter.Label(inputFrame, text = "맵의 가로 길이 입력")
YLabel = tkinter.Label(inputFrame, text = "맵의 세로 길이 입력")
positionLabel = tkinter.Label(inputFrame, text = "시작 좌표 입력 \nx,y의 형식으로")
sizeLabel = tkinter.Label(inputFrame, text = "플레이어 크기 입력 \nx,y의 형식으로")
jumpHeightLabel = tkinter.Label(inputFrame, text = "점프 높이 입력")
jumpTimeLabel = tkinter.Label(inputFrame, text = "점프 시간 입력")
mapNameAlert = tkinter.Label(inputFrame, text = "저장할 이름 입력")
speedLabel = tkinter.Label(inputFrame, text = "이동 속도 입력")

XEntry = tkinter.Entry(inputFrame)
YEntry = tkinter.Entry(inputFrame)
jumpHeight = tkinter.Entry(inputFrame)
jumpTime = tkinter.Entry(inputFrame)
mapName = tkinter.Entry(inputFrame)
speed = tkinter.Entry(inputFrame)
position = tkinter.Entry(inputFrame)
size = tkinter.Entry(inputFrame)

button = tkinter.Button(inputFrame, text = "확인", command = sizeChange)
saveButton = tkinter.Button(inputFrame, text = "저장", command = save)
#debugbutton = tkinter.Button(inputFrame, text = "배열 ", command = debug)
blackButton = tkinter.Button(inputFrame, command = blackBrush, bg = "black", width = 5)
redButton = tkinter.Button(inputFrame, command = redBrush, bg = "red", width = 5)
greenButton = tkinter.Button(inputFrame, command = greenBrush, bg = "green", width = 5)
blueButton = tkinter.Button(inputFrame, command = blueBrush, bg = "blue", width = 5)
yellowButton = tkinter.Button(inputFrame, command = yellowBrush, bg = "yellow", width = 5)
cyanButton = tkinter.Button(inputFrame, command = cyanBrush, bg = "cyan", width = 5)
magentaButton = tkinter.Button(inputFrame, command = magentaBrush, bg = "magenta", width = 5)
whiteButton = tkinter.Button(inputFrame, command = whiteBrush, bg = "white", width = 5)
grayButton = tkinter.Button(inputFrame, command = grayBrush, bg = "gray", width = 5)

canvas = tkinter.Canvas()

mapSizeAlert.grid()
XLabel.grid()
XEntry.grid()
YLabel.grid()
YEntry.grid()
button.grid()
#debugbutton.grid()

blackButton.grid()
redButton.grid()
greenButton.grid()
blueButton.grid()
yellowButton.grid()
cyanButton.grid()
magentaButton.grid()
whiteButton.grid()
grayButton.grid()

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