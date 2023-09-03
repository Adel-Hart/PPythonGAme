import main
import pygame
import ctypes
from multiprocessing import Process

def testPlay(mapName): #현재 temp 폴더에 있는 특정 맵을 새로운 창에서 플레이한다

    clear = 0
    while clear == 0: #사망했을시 계속 다시실행
        clear = main.runGame(f"./temp/{mapName}")

    

    return