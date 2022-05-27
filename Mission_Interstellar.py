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
vec = pygame.math.Vector2

MAX_SPEED = 5

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

class Player(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)

        (self.image, self.rect) = load_image('ship.png', 40,
                                             40, -1)
        self.original_image = self.image
        self.position = vec(pos)
        self.rect = self.image.get_rect(center=self.position)
        self.vel = vec(0, 0)
        self.acceleration = vec(0, -0.02)
        self.low_acceleration = vec(0, 0)
        self.angle_speed = 0
        self.angle = 0
        self.fuel = 0
        self.maxfuel = 0
        self.gameOver = False
        self.rect.center = pos

    def rotate(self):
        self.acceleration.rotate_ip(self.angle_speed)
        self.angle += self.angle_speed
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def checkbounds(self):
        global gameovermenu
        if self.rect.left > width:
            self.gameOver = True
        if self.rect.right < 0:
            self.gameOver = True
        if self.rect.top > height:
            self.gameOver = True
        if self.rect.bottom < 0:
            self.gameOver = True

    def update(self):
        self.checkbounds()
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.angle_speed = -1
            self.rotate()
            self.fuel -= 0.01
        if keys[K_RIGHT]:
            self.angle_speed = 1
            self.rotate()
            self.fuel -= 0.01
        if keys[K_UP]:
            self.vel += self.acceleration
            self.fuel -= 0.05
        if keys[K_DOWN]:
            self.vel -= self.acceleration
            self.fuel -= 0.05
        if keys[K_SPACE]:
            brake_vector = vec(-(self.vel.x * 0.1), -(self.vel.y * 0.1))
            self.vel += brake_vector
            self.fuel -= 0.1
        if keys[K_ESCAPE]:
            self.gameOver = True

        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        self.position += self.vel
        self.rect.center = self.position

        screen.blit(self.image, self.rect)


player = Player(screen.get_rect().center)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
    clock.tick(60)
