import tkinter

window=tkinter.Tk()
window.title("tkinter 테스트") #창의 이름
window.geometry("1200x800+100+100") #창의 너비, 높이
window.resizable(True, True) #창 크기 조절 가능 여부
#window.attributes("-fullscreen", True) #전체화면

inputFrame = tkinter.Frame(window, relief="solid", bd=2)
inputFrame.place(x = 0, y = 0)
gridFrame = tkinter.Frame(window, relief="solid", bd=2)
gridFrame.place(x = 400, y = 0)

mapX = 0
mapY = 0
gridSize = 4 #격자 한칸의 크기
mapArray = []
a = tkinter.Label()

def sizeChange(): #2차원 배열 크기 변경
    if entryX.get().isdigit() and entryY.get().isdigit(): 
        label.config(text = entryX.get() + ", " + entryY.get())
        global mapX
        global mapY
        global mapArray
        for i in gridFrame.grid_slaves():
            i.destroy()
        mapX = int(entryX.get())
        mapY = int(entryY.get())
        mapArray = [[0 for y in range(mapY)] for x in range(mapX)]
        drawgrid()
    else:
        label.config(text = "정수를 입력해주세요...!")

def drawgrid(): #격자 그리기
    global gridSize
    event = 0
    for x in range(mapX):
        for y in range(mapY):
            mapArray[x][y] = tkinter.Label(gridFrame, text = f"{x} {y}", width = gridSize * 2, height = gridSize, relief = "solid", borderwidth = 2, bg = "blue")
            #mapArray[x][y].bind("<Button-1>", colorChange)
            mapArray[x][y].grid(column = x + 4 , row = y + 4)

#def colorChange(event):
#    mapArray[x][y].config(bg = "red")
    
label = tkinter.Label(inputFrame, text = "")
entryX = tkinter.Entry(inputFrame)
entryY = tkinter.Entry(inputFrame)
button = tkinter.Button(inputFrame, text = "확인", command = sizeChange)

label.grid()
entryX.grid()
entryY.grid()
button.grid()

window.mainloop()