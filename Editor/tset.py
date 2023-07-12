import tkinter

window=tkinter.Tk()
window.title("tkinter 테스트") #창의 이름
window.geometry("1200x800+100+100") #창의 너비, 높이
window.resizable(True, True) #창 크기 조절 가능 여부
a = tkinter.Label()
def debug(a):
    print("엄준식")



def colorChange(parameter):
    a
    a.config(bg = "red")
    

a = tkinter.Label(window, text = "", width = 8, height = 4, relief = "solid", borderwidth = 2, bg = "blue")
a.bind("<Button-1>", colorChange)
a.grid(column = 4 , row = 4)

window.mainloop()