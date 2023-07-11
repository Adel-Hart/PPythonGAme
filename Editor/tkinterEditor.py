import tkinter

window=tkinter.Tk()

window.title("tkinter 테스트") #창의 이름
window.geometry("1200x800+100+100") #창의 너비, 높이
window.resizable(True, True) #창 크기 조절 가능 여부
#window.attributes("-fullscreen", True) #전체화면

mapX = 0
mapY = 0
mapArray = []

def integercheck(): #입력값으로 2차원 배열 크기 변경
    if entryX.get().isdigit() and entryY.get().isdigit(): 
        label.config(text = entryX.get() + ", " + entryY.get())
        global mapX
        global mapY
        global mapArray
        mapX = int(entryX.get())
        mapY = int(entryY.get())
        mapArray = [[0 for y in range(mapY)] for x in range(mapX)]
        asd()
    else:
        label.config(text = "정수를 입력해주세요...!")

def asd(): #격자 그리기

    for x in range(mapX):
        for y in range(mapY):
            mapArray[x][y] = tkinter.Label(window, text = "", width = 2, height = 1, relief = "solid", borderwidth = 2).grid(column=x+4 , row = y+4)
          


label = tkinter.Label(window, text = "곧 바뀔 텍스트")
entryX = tkinter.Entry(window)
entryY = tkinter.Entry(window)
button = tkinter.Button(window, text = "확인", command = integercheck)

label.grid()
entryX.grid()
entryY.grid()
button.grid()


window.mainloop()
