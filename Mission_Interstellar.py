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

def displaytext(
        text,
        fontsize,
        x,
        y,
        color,
):
    font = pygame.font.SysFont('sawasdee', fontsize, True)
    text = font.render(text, 1, color)
    textpos = text.get_rect(centerx=x, centery=y)
    screen.blit(text, textpos)
    return text


class stars:

    def __init__(self, radius, color, nofstars, speed=5):
        self.radius = radius
        self.color = color
        self.speed = speed
        self.nofstars = nofstars
        self.starpos = [[0 for j in range(2)] for i in range(self.nofstars)]
        for x in range(self.nofstars):
            self.starpos[x][0] = random.randrange(0, width)
            self.starpos[x][1] = random.randrange(0, height)

    def drawstars(self):
        for x in range(self.nofstars):
            pygame.draw.circle(screen, self.color, (self.starpos[x][0], self.starpos[x][1]), self.radius)
        self.movestars()

    def movestars(self):
        for x in range(self.nofstars):
            self.starpos[x] -= speed_vec
            if self.starpos[x][0] > width:
                self.starpos[x][0] = 0
            if self.starpos[x][0] < 0:
                self.starpos[x][0] = width
            if self.starpos[x][1] > height:
                self.starpos[x][1] = 0
            if self.starpos[x][1] < 0:
                self.starpos[x][1] = height


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

class Planets(pygame.sprite.Sprite):

    def __init__(self, radius, pos, target=False, translate=False):
        pygame.sprite.Sprite.__init__(self)

        if target:
            (self.image, self.rect) = load_image("target_planet.png", radius,
                                                 radius, -1)

        else:
            files = [f for f in listdir("Sprites/Planets") if
                     isfile(join("Sprites/Planets", f))]

            file = files[random.randrange(0, len(files))]

            (self.image, self.rect) = load_image(join("Planets", file), radius,
                                                 radius, -1)

        self.rect.center = pos
        self.radius = radius
        self.vicinity_rect = self.rect.inflate(radius * NORMAL_GRAVITY,
                                               radius * NORMAL_GRAVITY)
        self.vicinity_rect.center = self.rect.center
        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.translate = translate

    def update(self):
        if self.translate:
            self.pos -= speed_vec
            self.rect.center = self.pos
            self.vicinity_rect.center = self.rect.center

        screen.blit(self.image, self.rect)
        # if self.starpos[x][0] > width:
        #     self.starpos[x][0] = 0
        # if self.starpos[x][0] < 0:
        #     self.starpos[x][0] = width
        # if self.starpos[x][1] > height:
        #     self.starpos[x][1] = 0
        # if self.starpos[x][1] < 0:
        #     self.starpos[x][1] = height

    def drawplanets(self):
        # pygame.draw.circle(self.image, self.color, (self.planepos[0], self.planepos[1]), self.radius)
        screen.blit(self.image, self.rect)

class BlackHole(pygame.sprite.Sprite):

    def __init__(self, pos, radius, translate=False):
        pygame.sprite.Sprite.__init__(self)

        (self.image, self.rect) = load_image('blackhole.png', radius,
                                             radius * 0.45, -1)

        self.rect.center = pos
        self.pos = vec(pos)
        self.radius = radius
        self.vicinity_rect = self.rect.inflate(radius * 1.5, radius * 1.5)
        self.vicinity_rect.center = self.rect.center
        self.rect2 = self.rect
        self.rect2.width += 20
        self.rect2.height += 20
        self.rect2.center = self.rect.center
        self.translate = translate

    def update(self):
        if self.translate:
            self.pos -= speed_vec
            self.rect.center = self.pos
            self.vicinity_rect.center = self.rect.center
            self.rect2.center = self.rect.center

        screen.blit(self.image, self.rect)


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, pos, radius, rot_radius, offset, sign, angle_speed,
                 *groups, translate=False):
        super().__init__(*groups)
        files = [f for f in listdir("Sprites/Asteroids") if
                 isfile(join("Sprites/Asteroids", f))]

        file = files[random.randrange(0, len(files))]

        (self.image, self.rect) = load_image(join("Asteroids", file), radius,
                                             radius, -1)

        # self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = vec(pos)
        self.sign = sign
        if (self.sign == "-"):
            self.offset = vec(-rot_radius, offset)
        else:
            self.offset = vec(rot_radius, offset)
        self.angle = 0
        self.angle_speed = angle_speed
        self.translate = translate
        # self.angle_speed = random.randrange(2, 8)/10

    def update(self):
        if self.translate:
            self.pos -= speed_vec
            self.rect.center = self.pos

        if self.sign == "-":
            self.angle -= self.angle_speed
        else:
            self.angle += self.angle_speed
        self.rect.center = self.pos + self.offset.rotate(self.angle)

        screen.blit(self.image, self.rect)

    def destroy(self):
        self.kill()

class Meteor(pygame.sprite.Sprite):

    def __init__(self, pos, radius, speed):
        pygame.sprite.Sprite.__init__(self)
        files = [f for f in listdir("Sprites/Meteors") if
                 isfile(join("Sprites/Meteors", f))]

        file = files[random.randrange(0, len(files))]

        (self.image, self.rect) = load_image(join("Meteors", file), radius,
                                             radius, -1)

        self.rect = self.image.get_rect(center=pos)
        self.pos = vec(pos)
        self.speed = speed
        self.explosion_sound = pygame.mixer.Sound('Sprites/explosion.wav')
        self.explosion_sound.set_volume(0.1)
        self.initial_pos = pos

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        screen.blit(self.image, self.rect)
        self.pos += self.speed
        self.rect.center = self.pos
        if self.rect.left > screen.get_width():
            self.kill()
        if self.rect.top > screen.get_height():
            self.kill()
        # if self.rect.top < 100 and self.rect.top>0:
        #    self.meteor_sound.play()

    def recenter(self):
        self.pos = self.initial_pos
        self.rect.center = self.pos

    def destroy(self):
        (x, y) = self.rect.center
        if pygame.mixer.get_init():
            self.explosion_sound.play(maxtime=1000)

        self.explosion = Explosion(x, y, 60)
        for i in range(0, 30):
            self.explosion.update()

        self.kill()
        self.explosion.kill()


class WormHole(pygame.sprite.Sprite):

    def __init__(self, pos, angle, radius, translate=False):
        pygame.sprite.Sprite.__init__(self)

        (self.original_image, self.rect) = load_image('wormhole.jpg', radius,
                                                      radius * 0.45, white)

        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = pos
        self.radius = radius
        self.angle = angle
        self.pos = vec(pos)
        self.translate = translate

    def update(self):
        if self.translate:
            self.pos -= speed_vec
            self.rect.center = self.pos

        screen.blit(self.image, self.rect)


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

class flame(pygame.sprite.Sprite):

    def __init__(self, width, length, user, direction):
        pygame.sprite.Sprite.__init__(self)

        if direction == 1:
            (self.image, self.rect) = load_image('flame_up.png', width, length, -1)
        elif direction == 2:
            (self.image, self.rect) = load_image('flame_right.png', width, length, -1)
        elif direction == 3:
            (self.image, self.rect) = load_image('flame_left.png', width, length, -1)
        elif direction == 4:
            (self.image, self.rect) = load_image('flame_down.png', width, length, -1)

        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = user.rect.center

    def update(self, user):
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = user.rect.center
        self.image = pygame.transform.rotate(self.original_image, -user.angle)
        screen.blit(self.image, self.rect)

    def kill(self):
        self.kill()


player = Player(screen.get_rect().center)


def main_menu():
    print("Mainmenu")
    color_selected = blue
    color_normal = white
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    global mainmenu
    global submenu
    global settingsmenu
    global howtoplaymenu
    global running
    global speed_vec
    selected = 0
    while mainmenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected -= 1
                elif event.key == pygame.K_DOWN:
                    selected += 1

                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        mainmenu = False
                        submenu = True
                        level_menu()
                    if selected == 1:
                        mainmenu = False
                        settingsmenu = True
                        settings()
                    if selected == 2:
                        mainmenu = False
                        howtoplaymenu = True
                        howtoplay()
                    if selected == 3:
                        pygame.quit()
                        quit()

        screen.fill((0, 0, 0))
        displaytext('Play', 32, width / 2 - 20, height - 400, blue)
        displaytext('Options', 32, width / 2 - 20, height - 300, white)
        displaytext('How To Play', 32, width / 2 - 20, height - 200, white)
        displaytext('Exit', 32, width / 2 - 20, height - 100, white)

        if selected > 3:
            selected = 0
        if selected < 0:
            selected = 3

        if (selected == 0):
            displaytext('Play', 32, width / 2 - 20, height - 400,
                        color_selected)
            displaytext('Options', 32, width / 2 - 20, height - 300,
                        color_normal)
            displaytext('How To Play', 32, width / 2 - 20, height - 200,
                        color_normal)
            displaytext('Exit', 32, width / 2 - 20, height - 100, color_normal)
        elif (selected == 1):
            displaytext('Play', 32, width / 2 - 20, height - 400, color_normal)
            displaytext('Options', 32, width / 2 - 20, height - 300,
                        color_selected)
            displaytext('How To Play', 32, width / 2 - 20, height - 200,
                        color_normal)
            displaytext('Exit', 32, width / 2 - 20, height - 100, color_normal)
        elif (selected == 2):
            displaytext('Play', 32, width / 2 - 20, height - 400, color_normal)
            displaytext('Options', 32, width / 2 - 20, height - 300,
                        color_normal)
            displaytext('How To Play', 32, width / 2 - 20, height - 200,
                        color_selected)
            displaytext('Exit', 32, width / 2 - 20, height - 100, color_normal)
        elif (selected == 3):
            displaytext('Play', 32, width / 2 - 20, height - 400, color_normal)
            displaytext('Options', 32, width / 2 - 20, height - 300,
                        color_normal)
            displaytext('How To Play', 32, width / 2 - 20, height - 200,
                        color_normal)
            displaytext('Exit', 32, width / 2 - 20, height - 100,
                        color_selected)

        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 20,
                    white)
        displaytext('Made by: Vatsal Patel', 12, width - 80, height - 10,
                    white)
        speed_vec = vec(0, -1)
        starfield1.drawstars()
        starfield2.drawstars()
        pygame.display.update()
        clock.tick(60)


def level_menu():
    print("Submenu")
    color1 = blue
    color2 = white
    color3 = white
    color4 = white
    color5 = white

    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)

    global mainmenu
    global submenu
    global running
    global speed_vec
    global currentLvl
    selected = 0
    while submenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected -= 1
                elif event.key == pygame.K_DOWN:
                    selected += 1
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    mainmenu = True
                    submenu = False
                    main_menu()

                if event.key == pygame.K_RETURN:
                    submenu = False
                    running = True
                    currentLvl = selected
                    if selected == 0:
                        level_1()
                    if selected == 1:
                        level_2()
                    if selected == 2:
                        level_3()
                    if selected == 3:
                        level_4()
                    if selected == 4:
                        level_5()

        screen.fill((0, 0, 0))
        if selected > 4:
            selected = 0
        if selected < 0:
            selected = 4

        if (selected == 0):
            color1 = blue
            color2 = white
            color3 = white
            color4 = white
            color5 = white
        elif (selected == 1):
            color1 = white
            color2 = blue
            color3 = white
            color4 = white
            color5 = white
        elif (selected == 2):
            color1 = white
            color2 = white
            color3 = blue
            color4 = white
            color5 = white
        elif (selected == 3):
            color1 = white
            color2 = white
            color3 = white
            color4 = blue
            color5 = white
        elif (selected == 4):
            color1 = white
            color2 = white
            color3 = white
            color4 = white
            color5 = blue

        displaytext('Level 1', 32, width / 2 - 20, height - 500, color1)
        displaytext('Level 2', 32, width / 2 - 20, height - 450, color2)
        displaytext('Level 3', 32, width / 2 - 20, height - 400, color3)
        displaytext('Level 4', 32, width / 2 - 20, height - 350, color4)
        displaytext('Level 5', 32, width / 2 - 20, height - 300, color5)
        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 20,
                    white)
        displaytext('Made by: Vatsal Patel', 12, width - 80, height - 10,
                    white)

        speed_vec = vec(0, -1)
        starfield1.drawstars()
        starfield2.drawstars()
        pygame.display.update()
        clock.tick(60)

def game_over():
    color1 = blue
    color2 = white

    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)

    global mainmenu
    global running
    global speed_vec
    global currentLvl
    global gameovermenu
    selected = 0

    while gameovermenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected -= 1
                elif event.key == pygame.K_RIGHT:
                    selected += 1
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    mainmenu = True
                    gameovermenu = False
                    main_menu()

                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        gameovermenu = False
                        running = True
                        # player.gameOver = False
                        play_lvl()
                    if selected == 1:
                        mainmenu = True
                        gameovermenu = False
                        main_menu()

        screen.fill((0, 0, 0))
        if selected > 1:
            selected = 0
        if selected < 0:
            selected = 1

        if (selected == 0):
            color1 = blue
            color2 = white
        elif (selected == 1):
            color1 = white
            color2 = blue

        displaytext('Game Over', 64, width / 2, 100, white)
        displaytext('Play Again', 32, width / 3 - 20, height - 400, color1)
        displaytext('Main Menu', 32, 2 * width / 3 + 20, height - 400, color2)
        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 40,
                    white)
        displaytext('Made by: Vatsal Patel', 12, width - 80, height - 20,
                    white)

        speed_vec = vec(0, -1)
        starfield1.drawstars()
        starfield2.drawstars()
        pygame.display.update()
        clock.tick(60)

def lvl_finished():
    color1 = blue
    color2 = white

    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)

    global mainmenu
    global running
    global speed_vec
    global currentLvl
    global lvlfinishmenu
    selected = 0

    while lvlfinishmenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected -= 1
                elif event.key == pygame.K_RIGHT:
                    selected += 1
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    mainmenu = True
                    lvlfinishmenu = False
                    main_menu()

                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        lvlfinishmenu = False
                        running = True
                        # player.gameOver = False
                        currentLvl += 1
                        play_lvl()
                    if selected == 1:
                        mainmenu = True
                        lvlfinishmenu = False
                        main_menu()

        screen.fill((0, 0, 0))
        if selected > 1:
            selected = 0
        if selected < 0:
            selected = 1

        if (selected == 0):
            color1 = blue
            color2 = white
        elif (selected == 1):
            color1 = white
            color2 = blue

        displaytext('Level Complete', 64, width / 2, 100, white)
        displaytext('Next Level', 32, width / 3 - 20, height - 400, color1)
        displaytext('Main Menu', 32, 2 * width / 3 + 20, height - 400, color2)
        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 40,
                    white)
        displaytext('Made by: Vatsal Patel', 12, width - 80, height - 20,
                    white)

        speed_vec = vec(0, -1)
        starfield1.drawstars()
        starfield2.drawstars()
        pygame.display.update()
        clock.tick(60)


def play_lvl():
    global currentLvl

    if currentLvl > 4:
        currentLvl = 0
    if currentLvl < 0:
        currentLvl = 4

    if currentLvl == 0:
        level_1()
    elif currentLvl == 1:
        level_2()
    elif currentLvl == 2:
        level_3()
    elif currentLvl == 3:
        level_4()
    elif currentLvl == 4:
        level_5()



main_menu()