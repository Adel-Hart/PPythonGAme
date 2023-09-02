import main
import pygame
import ctypes

def testPlay(mapName): #현재 temp 폴더에 있는 특정 맵을 새로운 창에서 플레이한다

    pygame.init() # initialize pygame

    main.runGame(f"./temp/{mapName}")

    pygame.quit

    return