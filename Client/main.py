import pygame
import os
import math
import random
import time



'''
파이썬 게임 개발
! 2023 07 22 start


-김동훈


'''


pygame.init() # initialize pygame

size = [1000, 800] # set screen size
screen = pygame.display.set_mode(size) # set pygame screen to object "screen"

pygame.display.set_caption("AL1S") # set window's name a "AL1s" (quick fix)

done = False # set shutdown triger

clock = pygame.time.Clock() # set fps
clock.tick(120) # ! must multiply fps to move speed (cause difference of speed) !

while not done : # loop the game





