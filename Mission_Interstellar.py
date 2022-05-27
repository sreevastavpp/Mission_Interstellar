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


class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y, radius=-1):
        pygame.sprite.Sprite.__init__(self)
        sheet = pygame.image.load('Sprites/enemy_explode.png')
        self.images = []
        for i in range(0, 768, 48):
            rect = pygame.Rect((i, 0, 48, 48))
            image = pygame.Surface(rect.size)
            image = image.convert()
            colorkey = image.get_at((10, 10))
            image.set_colorkey(colorkey, RLEACCEL)

            image.blit(sheet, (0, 0), rect)
            if radius != -1:
                image = pygame.transform.scale(image, (radius, radius))

            self.images.append(image)


        print("len(self.images)")
        print(len(self.images))

        self.image = self.images[0]
        self.index = 0
        print("self.index")
        print(self.index)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        screen.blit(self.image, self.rect)
        pygame.display.update()

    def update(self):
        self.image = self.images[self.index]
        screen.blit(self.image, self.rect)
        pygame.display.update()
        print("self.index")
        print(self.index)
        print("len(self.images)")
        print(len(self.images))
        if self.index + 1 >= len(self.images):
            self.index = 0
        else:
            self.index += 1



class Player(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)

        (self.image, self.rect) = load_image('ship.png', 40,
                                             40, -1)
        # self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
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
        self.isGravity = False
        self.explosion_sound = pygame.mixer.Sound('Sprites/explosion.wav')
        self.explosion_sound.set_volume(0.1)
        self.flame_up = flame(40,80,self,1)
        self.flame_down = flame(40,80,self,4)
        self.flame_right = flame(40,40,self,3)
        self.flame_left = flame(40,40,self,2)
        self.rect.center = pos
        # screen.blit(self.image, self.rect)

    def rotate(self):
        # Rotate the acceleration vector.
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
            gameovermenu = True
            game_over()
        if self.rect.right < 0:
            self.gameOver = True
            gameovermenu = True
            game_over()
        if self.rect.top > height:
            self.gameOver = True
            gameovermenu = True
            game_over()
        if self.rect.bottom < 0:
            self.gameOver = True
            gameovermenu = True
            game_over()

    def update(self):
        self.checkbounds()
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.angle_speed = -1
            self.rotate()
            self.fuel -= 0.01
            self.flame_left.update(self)
        if keys[K_RIGHT]:
            self.angle_speed = 1
            self.rotate()
            self.fuel -= 0.01
            self.flame_right.update(self)
        if keys[K_UP]:
            self.vel += self.acceleration
            self.fuel -= 0.05
            self.flame_up.update(self)

        if keys[K_DOWN]:
            self.vel -= self.acceleration
            self.fuel -= 0.05
            self.flame_down.update(self)
        if keys[K_SPACE]:
            brake_vector = vec(-(self.vel.x * 0.1), -(self.vel.y * 0.1))
            self.vel += brake_vector
            self.fuel -= 0.1
            self.flame_up.update(self)
            self.flame_down.update(self)
            self.flame_right.update(self)
            self.flame_left.update(self)
        if keys[K_ESCAPE]:
            self.gameOver = True
            global gameovermenu
            gameovermenu = True
            game_over()

        # for event in pygame.event.get():
        #     if event.type == pygame.KEYUP:
                # if event.key == pygame.K_UP:
                #
                # if event.key == pygame.K_DOWN:
                # if event.key == pygame.K_LEFT:
                # if event.key == pygame.K_RIGHT:
                # if event.key == pygame.K_SPACE:

        # max speed
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        global speed_vec
        speed_vec = self.vel
        self.position += self.vel
        self.rect.center = self.position

        screen.blit(self.image, self.rect)


    def explode(self):
        (x, y) = self.rect.center
        if pygame.mixer.get_init():
            self.explosion_sound.play(maxtime=1000)

        self.explosion = Explosion(x, y, 60)
        for i in range(0,30):
            self.explosion.update()
        self.kill()
        self.explosion.kill()
        self.gameOver = True
        global gameovermenu
        gameovermenu = True

    def gravity(self, planet, gravity_const):
        # self.vel += self.low_acceleration
        # if(self.angle_speed>0):
        #     self.angle_speed = 0.5
        # else:
        #     self.angle_speed = -0.5
        gravity_const = gravity_const
        self.rotate()
        dx = self.position.x - planet.rect.centerx
        dy = self.position.y - planet.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance

        # distance = vec(self.rect.center).distance_to(planet.rect.center)
        if planet.radius * 0.5 < distance < planet.radius * gravity_const:
            angle_btw = vec(self.rect.center).angle_to(planet.rect.center)
            # print(angle_btw)
            # print(self.angle)
            # print(planet.radius*GRAVITY - distance)

            planet_distance = (planet.radius * gravity_const - distance)

            if self.vel.magnitude() < 0.5:
                angle_constant = gravity_const * 10 * planet_distance
            else:
                angle_constant = gravity_const * 20 * self.vel.magnitude() * planet_distance
            # print(self.vel.magnitude())

            if not 8 < abs(angle_btw) < 10:
                if planet.rect.left - self.rect.x > planet.rect.right - self.rect.x:
                    if 230 < self.angle or self.angle < 60:
                        self.angle_speed = (angle_btw * angle_constant) / planet.radius
                        # self.vel += self.low_acceleration
                    else:
                        self.angle_speed = -(angle_btw * angle_constant) / planet.radius
                        # self.vel -= self.low_acceleration
                else:
                    if 230 < self.angle or self.angle < 60:
                        self.angle_speed = -(angle_btw * NORMAL_GRAVITY * self.vel.magnitude() * 2) / planet.radius
                        # self.vel -= self.low_acceleration
                    else:
                        self.angle_speed = (angle_btw * NORMAL_GRAVITY * self.vel.magnitude() * 2) / planet.radius
                        # self.vel += self.low_acceleration

            # self.vel *= 1.009
            # move_dist = min(self.vel.magnitude(), dist)

            self.vel -= vec(dx, dy) * 0.02
            # global speed_vec
            # speed_vec = self.vel
            # self.position += self.vel
            # self.rect.center = self.position

            # if self.rect.x - planet.rect.top > self.rect.x - planet.rect.right:
            #     self.vel += self.low_acceleration
            # else:
            #     self.vel -= self.low_acceleration

        # self.isGravity = True
        # self.rect = self.image.get_rect(center=pos)
        # self.position = vec(pos)
        # offset = vec(100, 0)
        #
        # self.angle -= 2
        #
        # self.rotate()
        # self.rect.center = self.position + offset.rotate(self.angle)

    def addFuel(self, fuelstep):
        self.fuel += fuelstep
        for i in range(1000):
            i = i
        if self.fuel > self.maxfuel:
            self.fuel = self.maxfuel

player = Player(screen.get_rect().center)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
    clock.tick(60)
