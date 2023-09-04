import main
import pygame
import ctypes
from multiprocessing import Process
import pygetwindow

def testPlay(mapName): #현재 temp 폴더에 있는 특정 맵을 원래 pygame 창에서 플레이한다

    win = pygetwindow.getWindowsWithTitle("RGB")[0]
    win.activate()

    clear = 0
    while clear == 0: #사망했을시 계속 다시실행
        clear = main.runGame(f"./maps/{mapName}", "TestPlay")
    
    win = pygetwindow.getWindowsWithTitle("맵에디터")[0]
    win.activate()

    return