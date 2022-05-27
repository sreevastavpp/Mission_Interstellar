import os
import pygame
import sys
import time
import math
import random
from pygame.locals import *


pygame.init()

pygame.display.set_caption('Mission Interstellar')

size = (width, height) = (1024, 768)
screen = pygame.display.set_mode(size, DOUBLEBUF | FULLSCREEN)
clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
    clock.tick(60)
