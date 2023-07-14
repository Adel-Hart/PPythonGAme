# 유지보수하기 어렵게 코딩하는 방법

import tkinter
import pyautogui

window = tkinter.Tk()
window.title("tkinter 테스트") #창의 이름
window.geometry("1200x800+100+100") #창의 너비, 높이
window.resizable(False, False) #창 크기 조절 가능 여부
window.attributes("-fullscreen", True) #전체화면

inputFrame = tkinter.Frame(window, relief="solid", bd=2)
inputFrame.place(x = 0, y = 0)
gridFrame = tkinter.Frame(window, relief="solid", bd=2)
gridFrame.place(x = 600, y = 0)

colorTuple = ("black", "red", "green", "blue", "yellow", "cyan", "magenta", "white")
mapX = 0
mapY = 0
gridSize = 50 #격자 한칸의 크기
mapArray = []

def sizeChange(): #2차원 배열 크기 변경
    global mapX
    global mapY
    global mapArray
    global canvas
    if entryX.get().isdigit() and entryY.get().isdigit(): 
        label.config(text = entryX.get() + ", " + entryY.get())
        canvas.destroy()
        mapX = int(entryX.get())
        mapY = int(entryY.get())
        canvas = tkinter.Canvas(gridFrame, width = mapX * gridSize, height = mapY * gridSize)
        mapArray = [[0 for y in range(mapY)] for x in range(mapX)]
        drawGrid()
    else:
        label.config(text = "정수를 입력해주세요...!")

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
    mapArray[x][y] = 1
    canvas.create_rectangle(x * gridSize, y * gridSize, x * gridSize + gridSize, y * gridSize + gridSize, fill = colorTuple[1])

def debug():
    print(mapArray)

def click(event):
    print(pyautogui.position())

window.bind("<Button-1>", click)
label = tkinter.Label(inputFrame, text = "")
entryX = tkinter.Entry(inputFrame)
entryY = tkinter.Entry(inputFrame)
button = tkinter.Button(inputFrame, text = "확인", command = sizeChange)
debugbutton = tkinter.Button(inputFrame, text = "배열", command = debug)
canvas = tkinter.Canvas()

label.grid()
entryX.grid()
entryY.grid()
button.grid()
debugbutton.grid()

window.mainloop()