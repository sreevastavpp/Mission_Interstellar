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

def load_image(file, size_x=-1, size_y=-1, colorkey=None):
    path = os.path.join('Sprites', file)
    image = pygame.image.load(path)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if size_x != -1 or size_y != -1:
        image = pygame.transform.scale(image, (size_x, size_y))

    return image, image.get_rect()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
    clock.tick(60)
