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

        (self.image, self.rect) = load_image('Meteors/meteor.png', radius*0.7,
                                             2*radius, -1)
        self.original_image = self.image
        self.angle = round(math.atan2(speed.x, speed.y)/math.pi*180)
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
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

def level_1():
    global running
    global gameovermenu
    global lvlfinishmenu
    global speed_vec

    fuelbeep = False
    showintro = True
    player = Player((50, 50))
    player.gameOver = False
    player.angle_speed = 90
    player.rotate()
    player.fuel = 30
    player.maxfuel = 30
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    player.speed_vec = vec(0, 0)
    speed_vec = vec(0, 0)

    planetGroup = pygame.sprite.Group()

    planet2 = Planets(200, (100, 600))
    planet3 = Planets(250, (600, 700))
    planet4 = Planets(100, (300, 100))
    planet5 = Planets(125, (800, 200))
    target_planet = Planets(100, (1000, 500), True)

    planetGroup.add(planet2)
    planetGroup.add(planet3)
    planetGroup.add(planet4)
    planetGroup.add(planet5)

    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)

    while running and not player.gameOver:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                gameovermenu = True
                game_over()

        for planet in planetGroup:
            if pygame.sprite.collide_mask(player, planet):
                player.explode()

        if pygame.sprite.collide_mask(player, target_planet):
            if player.vel.magnitude() > 1:
                player.explode()
            else:
                thrust_on.stop()
                lvl_complete_effect.play()
                lvlfinishmenu = True
                player.gameOver = True
                lvl_finished()

        planet_collided_sprites = pygame.sprite.groupcollide(planetGroup,
                                                             playerGroup,
                                                             False, False,
                                                             collided=vicinity_collision)

        if len(planet_collided_sprites) != 0:
            for planet in planet_collided_sprites:
                player.gravity(planet, NORMAL_GRAVITY)

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()

        planetGroup.update()
        planetGroup.draw(screen)
        target_planet.update()
        player.update()

        if showintro:
            pygame.display.update()
            border = pygame.Rect((50, height - 100), (width - 100, 70))
            textbox = pygame.Rect((50, height - 100), (width - 100, 70))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)

            displayanimtext('TARS:', (60, 42.5))
            displayanimtext('Hello Captain Cooper. Earth is no more habitable, so you are directed to take the Endurance ship with 1000 frozen human embryos and reach the planet, Pandora.', (
                100, 42.5))  # text string and x, y coordinate tuple.
            displayanimtext('Our previous teams have landed there. You might find their spaceship. Are you ready to save humanity? ', (100, 43.5))
            displayanimtext('Press ENTER to continue', (800, 44.5))
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            # if setting_music:
                                # bg_music.play(-1)

        showfuelbar(player, [100, height - 20, player.fuel * (900/player.maxfuel), 10])


        if player.fuel <= 0:
            player.gameOver = True
            gameovermenu = True
            game_over()

        pygame.display.flip()
        clock.tick(60)

def createmeteorWave(num, posx):
    meteors = []
    mtg = pygame.sprite.Group()
    for i in range(num):
        randx = random.randrange(-200, screen.get_width()-200)
        randy = random.randrange(0, 100) - 150
        rand_rad = random.randrange(5, 30)
        rand_speedx = random.randrange(10, 30) / 10
        rand_speedy = random.randrange(10, 30) / 10
        meteor = Meteor((randx, randy), rand_rad,
                        vec(rand_speedx, rand_speedy))
        mtg.add(meteor)
        meteors.append(meteor)

    return meteors, mtg


def level_2():
    global running
    global gameovermenu
    global lvlfinishmenu
    global speed_vec
    showintro = True
    player = Player((50, 50))
    player.gameOver = False
    player.angle_speed = 90
    player.rotate()
    player.fuel = 20
    player.maxfuel = 20
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    player.speed_vec = vec(0, 0)
    speed_vec = vec(0, 0)
    start_time = None
    timercount = 1
    meteorWave = False
    meteorWarning = False

    meteors = []
    meteorGroup = pygame.sprite.Group()

    planetGroup = pygame.sprite.Group()

    # planet1 = Planets(100, (400, 450))
    planet2 = Planets(200, (250, 600))
    planet3 = Planets(150, (650, 200))
    planet4 = Planets(100, (250, 100))
    planet5 = Planets(125, (600, 700))
    target_planet = Planets(150, (900, 500), True)

    # meteor1 = Meteor((100,10), 50, vec(1,1), meteorGroup)
    # meteor2 = Meteor((200,20), 50, vec(1,1),meteorGroup)
    # meteor3 = Meteor((400,30), 50, vec(1,1),meteorGroup)
    # meteor4 = Meteor((500,40), 50, vec(1,1),meteorGroup)
    # meteor5 = Meteor((700,50), 50, vec(1,1),meteorGroup)
    # meteor6 = Meteor((700,50), 50, vec(1,1),meteorGroup)
    # meteor7 = Meteor((700,50), 50, vec(1,1),meteorGroup)
    # meteor8 = Meteor((700,50), 50, vec(1,1),meteorGroup)
    # meteor9 = Meteor((700,50), 50, vec(1,1),meteorGroup)
    # meteor10 = Meteor((700,50), 50, vec(1,1),meteorGroup)

    # planetGroup.add(planet1)
    planetGroup.add(planet2)
    planetGroup.add(planet3)
    planetGroup.add(planet4)
    planetGroup.add(planet5)
    # planetGroup.add(target_planet)

    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)

    asteroidGroup = pygame.sprite.Group()
    Asteroid(planet4.pos, 20, 90, 10, "-", 1.5, asteroidGroup)
    Asteroid(planet4.pos, 25, 100, -50, "+", 1, asteroidGroup)
    Asteroid(planet4.pos, 30, 105, 90, "-", 0.8, asteroidGroup)
    # asteroid4 = Asteroid(planet4.pos, 35, 110, -120, "+", 0.5, asteroidGroup)

    Asteroid(planet3.pos, 35, 160, 50, "-", 0.7, asteroidGroup)
    Asteroid(planet3.pos, 20, 100, 10, "-", 1.5, asteroidGroup)
    Asteroid(planet3.pos, 25, 100, -70, "+", 1, asteroidGroup)
    Asteroid(planet3.pos, 30, 120, 100, "+", 0.8, asteroidGroup)

    Asteroid(target_planet.pos, 30, 50, 100, "+", 0.8, asteroidGroup)
    Asteroid(target_planet.pos, 40, 120, -100, "-", 0.5, asteroidGroup)

    Asteroid(planet2.pos, 40, 150, -100, "+", 0.7, asteroidGroup)
    Asteroid(planet2.pos, 20, 100, -100, "-", 0.5, asteroidGroup)

    while running and not player.gameOver:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                gameovermenu = True
                game_over()

        for planet in planetGroup:
            if pygame.sprite.collide_mask(player, planet):
                player.explode()
        # if pygame.sprite.collide_mask(player, planet1):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet2):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet3):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet4):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet5):
        #     player.explode()
        if pygame.sprite.collide_mask(player, target_planet):
            if player.vel.magnitude() > 1:
                player.explode()
            else:
                thrust_on.stop()
                lvl_complete_effect.play()
                lvlfinishmenu = True
                player.gameOver = True
                lvl_finished()

        planet_collided_sprites = pygame.sprite.groupcollide(planetGroup,
                                                             playerGroup,
                                                             False, False,
                                                             collided=vicinity_collision)

        if len(planet_collided_sprites) != 0:
            for planet in planet_collided_sprites:
                player.gravity(planet, NORMAL_GRAVITY)

        for asteroid in asteroidGroup:
            if pygame.sprite.collide_mask(player, asteroid):
                player.explode()

        meteor_collided = pygame.sprite.groupcollide(meteorGroup, planetGroup,
                                                     False, False)
        if len(meteor_collided) != 0:
            for meteor in meteor_collided:
                meteorGroup.remove(meteor)
                meteors.remove(meteor)
                meteor.destroy()

        # meteor_collided_tgt = pygame.sprite.spritecollide(target_planet, meteorGroup, False)
        # if len(meteor_collided_tgt) != 0:
        #     for meteor in meteor_collided_tgt:
        #         meteor.destroy()

        for meteor in meteors:
            if pygame.sprite.collide_mask(player, meteor):
                player.explode()

            if pygame.sprite.collide_mask(target_planet, meteor):
                meteorGroup.remove(meteor)
                meteors.remove(meteor)
                meteor.destroy()

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()

        # planet2.update()
        # planet3.update()
        # planet4.update()
        # planet5.update()
        target_planet.update()
        # playerGroup.draw(screen)
        # planetGroup.draw(screen)
        planetGroup.update()
        planetGroup.draw(screen)
        # playerGroup.update()
        # asteroid1.update()
        # asteroid2.update()
        # asteroid3.update()
        asteroidGroup.update()
        asteroidGroup.draw(screen)
        # for meteor in meteors:
        #     meteor.draw()
        # meteor1.update()
        player.update()

        if showintro:
            pygame.display.update()
            border = pygame.Rect((50, height - 100), (width - 100, 70))
            textbox = pygame.Rect((50, height - 100), (width - 100, 70))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext('Heyy Captain Cooper it seems you are ready for the next mission. Your next mission is to land on the Krypton planet. Due to the asteroids and meteors, our previous', (
                60, 42.5))  # text string and x, y coordinate tuple.
            displayanimtext('team crashed before reaching there. If you find the planet habitable drop the rover, and base station and send SOS signal. Keep the hope alive.', (60, 43.5))
            displayanimtext('Press ENTER to continue', (800, 44.5))
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            start_time = pygame.time.get_ticks()
                            if setting_music:
                                bg_music.play(-1)

        if start_time:
            time_since_enter = pygame.time.get_ticks() - start_time
            if time_since_enter % 20000 > 15000:
                meteorWarning = True

            if time_since_enter / 20000 > timercount:
                timercount += 1
                meteorWarning = False
                meteorWave = True
                global warning_effect
                warning_effect.play()
                meteors, meteorGroup = createmeteorWave(15,
                                                        player.rect.centerx)
                # for meteor in meteors:
                #     meteorGroup.add(meteor)

            # message = 'Milliseconds since enter: ' + str(time_since_enter)
            # displaytext(message, 20, 100, 100, white)
            # count = 'Count: ' + str(timercount)
            # displaytext(count, 20, 100, 100, white)


        if player.fuel <= 0:
            player.gameOver = True
            gameovermenu = True
            game_over()

        showfuelbar(player, [100, height - 20, player.fuel * (900/player.maxfuel), 10])

        # for m in meteors:
        #     m.update()
        if meteorWarning:
            showMeteorWarning()
        if meteorWave:
            # displaytext("Meteor Shower", 30, screen.get_rect().centerx,
            #             screen.get_rect().centery, white)
            for m in meteors:
                m.update()
            if len(meteorGroup) == 0:
                meteorWave = False
        pygame.display.flip()
        clock.tick(60)

def level_3():
    global running
    global gameovermenu
    global lvlfinishmenu
    global speed_vec

    showintro = True
    player = Player((50, 50))
    player.gameOver = False
    player.angle_speed = 90
    player.rotate()
    player.fuel = 20
    player.maxfuel = 20
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    player.speed_vec = vec(0, 0)
    speed_vec = vec(0, 0)

    planetGroup = pygame.sprite.Group()

    # planet1 = Planets(100, (400, 450))
    planet2 = Planets(200, (100, 600))
    planet3 = Planets(250, (600, 700))
    planet4 = Planets(100, (300, 100))
    planet5 = Planets(125, (750, 250))
    target_planet = Planets(100, (900, 500), True)

    # planetGroup.add(planet1)
    planetGroup.add(planet2)
    planetGroup.add(planet3)
    planetGroup.add(planet4)
    planetGroup.add(planet5)

    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)

    blackhole = BlackHole(screen.get_rect().center, 300)
    blackholeGroup = pygame.sprite.Group()
    blackholeGroup.add(blackhole)

    while running and not player.gameOver:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                gameovermenu = True
                game_over()

        # if pygame.sprite.collide_mask(player, planet1):
        #     player.explode()
        for planet in planetGroup:
            if pygame.sprite.collide_mask(player, planet):
                player.explode()
        # if pygame.sprite.collide_mask(player, planet3):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet4):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet5):
        #     player.explode()
        if pygame.sprite.collide_mask(player, target_planet):
            if player.vel.magnitude() > 1:
                player.explode()
            else:
                thrust_on.stop()
                lvl_complete_effect.play()
                lvlfinishmenu = True
                player.gameOver = True
                lvl_finished()

        planet_collided_sprites = pygame.sprite.groupcollide(planetGroup,
                                                             playerGroup,
                                                             False, False,
                                                             collided=vicinity_collision)

        if len(planet_collided_sprites) != 0:
            for planet in planet_collided_sprites:
                player.gravity(planet, NORMAL_GRAVITY)

        blackhole_collided_sprites = pygame.sprite.groupcollide(blackholeGroup,
                                                                playerGroup,
                                                                False, False,
                                                                collided=vicinity_collision)
        if len(blackhole_collided_sprites) != 0:
            for b in blackhole_collided_sprites:
                player.gravity(b, BLACK_HOLE_GRAVITY)


        # blackhole_collided_sprites2 = pygame.sprite.groupcollide(blackholeGroup,
        #                                                         playerGroup,
        #                                                         False, False,
        #                                                         collided=blackhole_collision)
        # if len(blackhole_collided_sprites2) != 0:
        #     for b in blackhole_collided_sprites2:

        if pygame.sprite.collide_mask(player, blackhole):
            # blackhole_effect.play()
            player.explode(True)
            # blackhole_effect.play()

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()

        planet2.update()
        planet3.update()
        planet4.update()
        planet5.update()
        target_planet.update()
        # playerGroup.draw(screen)
        # planetGroup.draw(screen)
        # planetGroup.update()
        # playerGroup.update()
        blackhole.update()
        player.update()

        if showintro:
            pygame.display.update()
            border = pygame.Rect((50, height - 100), (width - 100, 80))
            textbox = pygame.Rect((50, height - 100), (width - 100, 80))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext(
                'Good to see you, Captain Cooper. Since you are so experienced a critical mission has been assigned to you that no one has endeavoured. There is a Cybertron planet on',
                (
                    60, 42.5))  # text string and x, y coordinate tuple.
            displayanimtext(
                'the far end of our galaxy. It is believed that intelligent species exist on Cybertron. Try to communicate with them to help humans. You will also encounter a massive',
                (60, 43.5))
            displayanimtext('Blackhole in the path, the biggest in the milky way. Avoid going near it.', (60, 44.5))
            displayanimtext('Press ENTER to continue', (800, 45.5))
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            if setting_music:
                                bg_music.play(-1)

        showfuelbar(player, [100, height - 20, player.fuel*(900/player.maxfuel), 10])

        if player.fuel <= 0:
            player.gameOver = True
            gameovermenu = True
            game_over()

        pygame.display.flip()
        clock.tick(60)


def level_4():
    global running
    global gameovermenu
    global lvlfinishmenu
    global speed_vec

    showintro = True
    player = Player((50, 50))
    player.gameOver = False
    player.angle_speed = 90
    player.rotate()
    player.fuel = 20
    player.maxfuel = 20
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    player.speed_vec = vec(0, 0)
    speed_vec = vec(0, 0)

    planetGroup = pygame.sprite.Group()

    planet1 = Planets(100, (550, 400))
    planet2 = Planets(200, (150, 550))
    planet3 = Planets(250, (600, 700))
    planet4 = Planets(100, (300, 100))
    planet5 = Planets(125, (650, 150))
    target_planet = Planets(150, (900, 500), True)
    start_time = None
    meteor_time = None
    meteorWarning = False
    meteorWave = False
    wormhole_travel = False
    meteors = []
    meteorGroup = pygame.sprite.Group()
    timercount = 1

    planetGroup.add(planet1)
    planetGroup.add(planet2)
    planetGroup.add(planet3)
    planetGroup.add(planet4)
    planetGroup.add(planet5)

    asteroidGroup = pygame.sprite.Group()
    Asteroid(planet1.pos, 20, 70, 10, "-", 1.5, asteroidGroup)
    Asteroid(planet1.pos, 25, 60, -70, "+", 1.2, asteroidGroup)
    Asteroid(planet1.pos, 30, 70, 100, "+", 1, asteroidGroup)

    Asteroid(planet5.pos, 20, 80, 10, "-", 1.5, asteroidGroup)
    Asteroid(planet5.pos, 25, 100, -70, "+", 1.2, asteroidGroup)
    Asteroid(planet5.pos, 30, 120, 100, "+", 1, asteroidGroup)

    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)

    wormhole1 = WormHole((150, 350), 0, 100)
    wormhole2 = WormHole((900, 250), -100, 100)
    wormholeGroup = pygame.sprite.Group()
    wormholeGroup.add(wormhole1)
    wormholeGroup.add(wormhole2)

    while running and not player.gameOver:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                gameovermenu = True
                game_over()

        # if pygame.sprite.collide_mask(player, planet1):
        #     player.explode()
        for planet in planetGroup:
            if pygame.sprite.collide_mask(player, planet):
                player.explode()
        # if pygame.sprite.collide_mask(player, planet3):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet4):
        #     player.explode()
        # if pygame.sprite.collide_mask(player, planet5):
        #     player.explode()
        if pygame.sprite.collide_mask(player, target_planet):
            if player.vel.magnitude() > 1:
                player.explode()
            else:
                thrust_on.stop()
                lvl_complete_effect.play()
                lvlfinishmenu = True
                player.gameOver = True
                lvl_finished()

        planet_collided_sprites = pygame.sprite.groupcollide(planetGroup,
                                                             playerGroup,
                                                             False, False,
                                                             collided=vicinity_collision)

        if len(planet_collided_sprites) != 0:
            for planet in planet_collided_sprites:
                player.gravity(planet, NORMAL_GRAVITY)

        meteor_collided = pygame.sprite.groupcollide(meteorGroup, planetGroup,
                                                     False, False)
        if len(meteor_collided) != 0:
            for meteor in meteor_collided:
                meteors.remove(meteor)
                meteorGroup.remove(meteor)
                meteor.destroy()

        for meteor in meteors:
            if pygame.sprite.collide_mask(player, meteor):
                player.explode()

            if pygame.sprite.collide_mask(target_planet, meteor):
                meteors.remove(meteor)
                meteorGroup.remove(meteor)
                meteor.destroy()

            if pygame.sprite.collide_mask(meteor, wormhole1):
                meteor.pos = wormhole2.rect.center
                meteor.speed.rotate_ip(-wormhole2.angle)

            if pygame.sprite.collide_mask(meteor, wormhole2):
                meteor.pos = wormhole1.rect.center
                meteor.speed.rotate_ip(-wormhole2.angle)
        # wormhole_collided_sprites = pygame.sprite.groupcollide(wormholeGroup,
        #                                                      playerGroup,
        #                                                      False, False,
        #                                                      collided=vicinity_collision)
        # if len(wormhole_collided_sprites) != 0:
        #     for w in wormhole_collided_sprites:
        #         player.gravity(w, BLACK_HOLE_GRAVITY)

        if pygame.sprite.collide_mask(player, wormhole1):
            if not wormhole_travel:
                thrust_on.stop()
                wormhole_effect.play()
                player.position = vec(wormhole2.rect.centerx,
                                      wormhole2.rect.centery)
                wormhole_travel = True
                start_time = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = -wormhole2.angle
                player.rotate()
                player.vel.rotate_ip(-wormhole2.angle)
                player.vel += player.acceleration

        if pygame.sprite.collide_mask(player, wormhole2):
            if not wormhole_travel:
                thrust_on.stop()
                wormhole_effect.play()
                wormhole_effect.play()
                player.position = vec(wormhole1.rect.centerx,
                                      wormhole1.rect.centery)
                wormhole_travel = True
                start_time = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = -wormhole2.angle
                player.rotate()
                player.vel.rotate_ip(-wormhole2.angle)
                player.vel += player.acceleration

        for asteroid in asteroidGroup:
            if pygame.sprite.collide_mask(player, asteroid):
                player.explode()

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()

        # planet2.update()
        # planet3.update()
        # planet4.update()
        # planet5.update()
        target_planet.update()
        planetGroup.update()
        planetGroup.draw(screen)
        asteroidGroup.update()
        asteroidGroup.draw(screen)
        wormholeGroup.update()
        wormholeGroup.draw(screen)
        meteorGroup.update()
        meteorGroup.draw(screen)
        player.update()

        if showintro:
            pygame.display.update()
            border = pygame.Rect((50, height - 100), (width - 100, 80))
            textbox = pygame.Rect((50, height - 100), (width - 100, 80))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext('Captain Cooper, there is bad news. The fuel tank was damaged by the black hole and a large amount of fuel leaked. We need to head towards Solaris about 2 lightyears', (
                60, 42.5))  # text string and x, y coordinate tuple.
            displayanimtext('away. We cannot reach Solaris with low fuel, so I found a wormhole in the path that can shorten our journey. Our previous team almost reached Solaris but was pulled due', (60, 43.5))
            displayanimtext('to the strong magnetic fields at the other end of the wormhole, so be careful. Hoping to reach without collision.', (60, 44.5))
            displayanimtext('Press ENTER to continue', (800, 45.5))
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            meteor_time = pygame.time.get_ticks()
                            # if setting_music:
                                # bg_music.play(-1)

        if meteor_time:
            time_since_enter = pygame.time.get_ticks() - meteor_time
            if time_since_enter % 20000 > 15000:
                meteorWarning = True

            if time_since_enter / 20000 > timercount:
                timercount += 1
                meteorWarning = False
                meteorWave = True
                global warning_effect
                warning_effect.play()
                meteors, meteorGroup = createmeteorWave(15,
                                                        player.rect.centerx)

        if meteorWarning:
            showMeteorWarning()
        if meteorWave:
            # displaytext("Meteor Shower", 30, screen.get_rect().centerx,
            #             screen.get_rect().centery, white)
            for m in meteors:
                m.update()
            if len(meteorGroup) == 0:
                meteorWave = False

        showfuelbar(player, [100, height - 20, player.fuel*(900/player.maxfuel), 10])

        if player.fuel <= 0:
            player.gameOver = True
            gameovermenu = True
            game_over()

        if wormhole_travel:
            if pygame.time.get_ticks() - start_time > 3000:
                wormhole_travel = False
                player.angle_speed = 0
            if player.vel.length() < 0.5:
                player.vel += player.acceleration

        pygame.display.flip()
        clock.tick(60)

def offset(offset, planetGroup, wormholeGroup, meteorGroup, blackholeGroup, asteroidGroup, target_pt, shipGroup, player, withplayer= False):
    for planet in planetGroup:
        planet.pos.x -= offset

    for wormhole in wormholeGroup:
        wormhole.pos.x -= offset

    for meteor in meteorGroup:
        meteor.pos.x -= offset

    for blackhole in blackholeGroup:
        blackhole.pos.x -= offset

    for asteroid in asteroidGroup:
        asteroid.pos.x -= offset

    for ship in shipGroup:
        ship.pos.x -= offset

    target_pt.pos.x -= offset

    if withplayer:
        player.position.x -= offset
        player.rect.centerx -= offset

    pygame.display.update()


def level_5():
    global running
    global gameovermenu
    global lvlfinishmenu
    global speed_vec

    showintro = True
    player = Player((50, 300), translate=True)
    player.gameOver = False
    player.angle_speed = 90
    player.rotate()
    player.fuel = 150
    player.maxfuel = 150
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    player.speed_vec = vec(0, 0)
    speed_vec = vec(0, 0)
    start_time1 = None
    start_time2 = None
    start_time3 = None
    meteor_time = None
    meteorWarning = False
    meteorWave = False
    wormhole_travel1 = False
    wormhole_travel2 = False
    wormhole_travel3 = False
    meteors = []
    meteorGroup = pygame.sprite.Group()
    timercount = 1

    wormhole1 = WormHole((3200, 400), 0, 100, translate=True)
    wormhole2 = WormHole((2000, 350), -100, 100, translate=True)
    wormhole3 = WormHole((3200, 200), 180, 100, translate=True)
    wormhole4 = WormHole((4100, 400), -100, 100, translate=True)
    wormhole5 = WormHole((3200, 600), -180, 100, translate=True)
    wormhole6 = WormHole((4300, 500), 100, 100, translate=True)

    wormholeGroup = pygame.sprite.Group()
    wormholeGroup.add(wormhole1)
    wormholeGroup.add(wormhole2)
    wormholeGroup.add(wormhole3)
    wormholeGroup.add(wormhole4)
    wormholeGroup.add(wormhole5)
    wormholeGroup.add(wormhole6)

    blackhole1 = BlackHole((2500, 400), 500, translate=True)
    blackhole2 = BlackHole((3850, 350), 200, translate=True)
    blackholeGroup = pygame.sprite.Group()
    blackholeGroup.add(blackhole1)
    blackholeGroup.add(blackhole2)

    planetGroup = pygame.sprite.Group()

    # planet1 = Planets(100, (450, 450), translate=True)
    planet2 = Planets(200, (150, 550), translate=True)
    planet3 = Planets(250, (600, 650), translate=True)
    planet4 = Planets(100, (300, 100), translate=True)
    planet5 = Planets(125, (650, 150), translate=True)
    planet11 = Planets(100, (1000, 200), translate=True)

    planet6 = Planets(100, (1000, 500), translate=True)
    planet7 = Planets(200, (1500, 200), translate=True)
    planet8 = Planets(250, (1400, 700), translate=True)
    planet9 = Planets(100, (1800, 550), translate=True)
    planet10 = Planets(125, (1900, 100), translate=True)

    planet12 = Planets(100, (4200, 450), translate=True)
    planet16 = Planets(200, (3550, 550), translate=True)
    planet13 = Planets(250, (4100, 700), translate=True)
    planet14 = Planets(100, (3700, 100), translate=True)
    planet15 = Planets(125, (4050, 200), translate=True)
    target_planet = Planets(300, (5200, 500), target=True, translate=True)

    planet16 = Planets(200, (200, -300), translate=True)
    planet17 = Planets(300, (600, -250), translate=True)
    planet18 = Planets(250, (1100, -200), translate=True)
    planet19 = Planets(150, (1500, -100), translate=True)
    planet20 = Planets(200, (1800, -250), translate=True)
    planet21 = Planets(300, (2200, -250), translate=True)
    planet22 = Planets(250, (2700, -200), translate=True)
    planet23 = Planets(150, (3100, -100), translate=True)
    planet24 = Planets(200, (3400, -250), translate=True)
    planet25 = Planets(300, (3800, -250), translate=True)
    planet26 = Planets(250, (4300, -200), translate=True)
    planet27 = Planets(200, (200, 900), translate=True)
    planet28 = Planets(300, (600, 1100), translate=True)
    planet29 = Planets(250, (1100, 1100), translate=True)
    planet30 = Planets(150, (1500, 1000), translate=True)
    planet31 = Planets(200, (1800, 1050), translate=True)
    planet32 = Planets(300, (2200, 1200), translate=True)
    planet33 = Planets(250, (2700, 1100), translate=True)
    planet34 = Planets(150, (3100, 1000), translate=True)
    planet35 = Planets(200, (3400, 1050), translate=True)
    planet36 = Planets(300, (3800, 1200), translate=True)
    planet37 = Planets(250, (4300, 1100), translate=True)
    planet38 = Planets(200, (-200, 200), translate=True)
    planet39 = Planets(300, (-200, 600), translate=True)
    planet40 = Planets(250, (-200, 1000), translate=True)
    planet41 = Planets(200, (-200, -100), translate=True)
    planetGroup.add(planet16)
    planetGroup.add(planet17)
    planetGroup.add(planet18)
    planetGroup.add(planet19)
    planetGroup.add(planet20)
    planetGroup.add(planet21)
    planetGroup.add(planet22)
    planetGroup.add(planet23)
    planetGroup.add(planet24)
    planetGroup.add(planet25)
    planetGroup.add(planet26)
    planetGroup.add(planet27)
    planetGroup.add(planet28)
    planetGroup.add(planet29)
    planetGroup.add(planet30)
    planetGroup.add(planet31)
    planetGroup.add(planet32)
    planetGroup.add(planet33)
    planetGroup.add(planet34)
    planetGroup.add(planet35)
    planetGroup.add(planet36)
    planetGroup.add(planet37)
    planetGroup.add(planet38)
    planetGroup.add(planet39)
    planetGroup.add(planet40)
    planetGroup.add(planet41)


    # planetGroup.add(planet1)
    planetGroup.add(planet11)
    planetGroup.add(planet2)
    planetGroup.add(planet3)
    planetGroup.add(planet4)
    planetGroup.add(planet5)
    planetGroup.add(planet6)
    planetGroup.add(planet7)
    planetGroup.add(planet8)
    planetGroup.add(planet9)
    planetGroup.add(planet10)
    planetGroup.add(planet12)
    planetGroup.add(planet13)
    planetGroup.add(planet14)
    planetGroup.add(planet15)
    planetGroup.add(planet16)

    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)

    asteroidGroup = pygame.sprite.Group()
    Asteroid(planet6.pos, 20, 90, 10, "-", 1.5, asteroidGroup, translate=True)
    Asteroid(planet6.pos, 25, 100, -50, "+", 1, asteroidGroup, translate=True)
    Asteroid(planet6.pos, 30, 105, 90, "-", 0.8, asteroidGroup, translate=True)

    Asteroid(planet10.pos, 35, 160, 50, "-", 0.7, asteroidGroup,
             translate=True)
    Asteroid(planet10.pos, 20, 100, 10, "-", 1.5, asteroidGroup,
             translate=True)
    Asteroid(planet10.pos, 25, 100, -70, "+", 1, asteroidGroup, translate=True)
    Asteroid(planet10.pos, 30, 120, 100, "+", 0.8, asteroidGroup,
             translate=True)

    Asteroid(planet8.pos, 30, 50, 180, "+", 0.8, asteroidGroup, translate=True)
    Asteroid(planet8.pos, 40, 120, -130, "-", 0.5, asteroidGroup,
             translate=True)

    Asteroid(planet7.pos, 40, 150, -100, "+", 0.7, asteroidGroup,
             translate=True)
    Asteroid(planet7.pos, 20, 100, -100, "-", 0.5, asteroidGroup,
             translate=True)

    Asteroid(blackhole2.pos, 30, 100, -80, "-", 1, asteroidGroup,
             translate=True)
    Asteroid(blackhole2.pos, 35, 110, 120, "+", 0.9, asteroidGroup,
             translate=True)

    shipGroup = pygame.sprite.Group()

    files = [f for f in listdir("Sprites/Spaceship") if
             isfile(join("Sprites/Spaceship", f))]

    image, rect = load_image(join("Spaceship", files[0]), 50,
                                         50, -1)
    ship = Ship(image, rect, (4400, 600), 100, 200, translate=True)
    shipGroup.add(ship)

    # image, rect = load_image(join("Spaceship", files[1]), 100,
    #                                      50, -1)
    # ship = Ship(image, rect, (4800, 200), -170, 200, translate=True)
    # shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[2]), 70,
                                         35, -1)
    ship = Ship(image, rect, (4600, 500), -40, 200, translate=True)
    shipGroup.add(ship)

    # image, rect = load_image(join("Spaceship", files[3]), 100,
    #                                      50, -1)
    # ship = Ship(image, rect, (5000, 200), 0, 200, translate=True)
    # shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[4]), 150,
                                         50, -1)
    ship = Ship(image, rect, (4900, 300), 0, 200, translate=True)
    shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[5]), 150,
                                         150, -1)
    ship = Ship(image, rect, (4500, 200), 0, 200, translate=True)
    shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[6]), 150,
                                         170, -1)
    ship = Ship(image, rect, (5200, 250), 0, 200, translate=True)
    shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[7]), 50,
                                         37, -1)
    ship = Ship(image, rect, target_planet.pos, 0, 170, -100, "-", 0.1, translate=True,rotate=True)
    shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[8]), 100,
                                         100, -1)
    ship = Ship(image, rect, (4700, 400), -20, 200, translate=True)
    shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[9]), 50,
                                         50, -1)
    ship = Ship(image, rect, (4900, 600), 0, 200, translate=True)
    shipGroup.add(ship)

    while running and not player.gameOver:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                final_lvl_music.stop()
                running = False
                gameovermenu = True
                game_over()


        if pygame.sprite.collide_mask(player, wormhole2):
            print("wormhole_travel1")
            print(wormhole_travel1)
            if not wormhole_travel1:
                thrust_on.stop()
                wormhole_effect.play()
                offset(wormhole1.rect.centerx - wormhole2.rect.centerx, planetGroup, wormholeGroup, meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup, player)
                player.position.y = wormhole1.rect.centery
                wormhole_travel1 = True
                start_time1 = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = wormhole2.angle
                player.rotate()
                player.vel.rotate_ip(wormhole2.angle)
                player.vel += player.acceleration

        if pygame.sprite.collide_mask(player, wormhole1):
            if not wormhole_travel1:
                thrust_on.stop()
                wormhole_effect.play()
                offset(wormhole2.rect.centerx - wormhole1.rect.centerx, planetGroup, wormholeGroup, meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup, player)
                player.position.y = wormhole2.rect.centery
                wormhole_travel1 = True
                start_time1 = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = -wormhole2.angle
                player.rotate()
                player.vel.rotate_ip(-wormhole2.angle)
                player.vel += player.acceleration

        if pygame.sprite.collide_mask(player, wormhole3):
            if not wormhole_travel2:
                thrust_on.stop()
                wormhole_effect.play()
                offset(wormhole4.rect.left - wormhole3.rect.centerx, planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup, player)
                player.position.y = wormhole4.rect.centery
                wormhole_travel2 = True
                start_time2 = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = wormhole4.angle
                player.rotate()
                player.vel.rotate_ip(wormhole4.angle)
                player.vel += player.acceleration

        if pygame.sprite.collide_mask(player, wormhole4):
            if not wormhole_travel2:
                thrust_on.stop()
                wormhole_effect.play()
                offset(wormhole3.rect.centerx - wormhole4.rect.centerx, planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup, player)
                player.position.y = wormhole3.rect.centery
                wormhole_travel2 = True
                start_time2 = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = -wormhole4.angle
                player.rotate()
                player.vel.rotate_ip(-wormhole4.angle)
                player.vel += player.acceleration

        if pygame.sprite.collide_mask(player, wormhole5):
            if not wormhole_travel3:
                thrust_on.stop()
                wormhole_effect.play()
                offset(wormhole6.rect.centerx - wormhole5.rect.centerx + 50, planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup, player)
                player.position.y = wormhole6.rect.centery
                wormhole_travel3 = True
                start_time3 = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = -wormhole6.angle
                player.rotate()
                player.vel.rotate_ip(-wormhole6.angle)
                player.vel += player.acceleration

        if pygame.sprite.collide_mask(player, wormhole6):
            if not wormhole_travel3:
                thrust_on.stop()
                wormhole_effect.play()
                offset(wormhole5.rect.centerx - wormhole6.rect.centerx, planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup, player)
                player.position.y = wormhole5.rect.centery
                wormhole_travel3 = True
                start_time3 = pygame.time.get_ticks()
                player.throughWormhole = True
                player.angle_speed = wormhole6.angle
                player.rotate()
                player.vel.rotate_ip(wormhole6.angle)
                player.vel += player.acceleration



        for planet in planetGroup:
            if pygame.sprite.collide_mask(player, planet):
                player.explode()

        for ship in shipGroup:
            if pygame.sprite.collide_mask(player, ship):
                player.explode()

        if pygame.sprite.collide_mask(player, target_planet):
            if player.vel.magnitude() > 1:
                player.explode()
            else:
                final_lvl_music.stop()
                thrust_on.stop()
                game_complete_effect.play()
                lvlfinishmenu = True
                player.gameOver = True
                lvl_finished()

        planet_collided_sprites = pygame.sprite.groupcollide(planetGroup,
                                                             playerGroup,
                                                             False, False,
                                                             collided=vicinity_collision)

        if len(planet_collided_sprites) != 0:
            for planet in planet_collided_sprites:
                player.gravity(planet, NORMAL_GRAVITY)

        blackhole_collided_sprites = pygame.sprite.groupcollide(blackholeGroup,
                                                                playerGroup,
                                                                False, False,
                                                                collided=vicinity_collision)
        if len(blackhole_collided_sprites) != 0:
            for b in blackhole_collided_sprites:
                player.gravity(b, BLACK_HOLE_GRAVITY)

        for blackhole in blackholeGroup:
            if pygame.sprite.collide_mask(player, blackhole):
                player.explode(True)

        meteor_collided = pygame.sprite.groupcollide(meteorGroup, planetGroup,
                                                     False, False)

        if len(meteor_collided) != 0:
            for meteor in meteor_collided:
                meteors.remove(meteor)
                meteorGroup.remove(meteor)
                meteor.destroy()

        meteor_collided = pygame.sprite.groupcollide(meteorGroup, shipGroup,
                                                     False, False)
        if len(meteor_collided) != 0:
            for meteor in meteor_collided:
                meteors.remove(meteor)
                meteorGroup.remove(meteor)
                meteor.destroy()

        meteor_collided = pygame.sprite.groupcollide(meteorGroup, blackholeGroup,
                                                     False, False)
        if len(meteor_collided) != 0:
            for meteor in meteor_collided:
                meteors.remove(meteor)
                meteorGroup.remove(meteor)
                meteor.destroy()

        for meteor in meteors:
            if pygame.sprite.collide_mask(player, meteor):
                player.explode()

            if pygame.sprite.collide_mask(target_planet, meteor):
                meteors.remove(meteor)
                meteorGroup.remove(meteor)
                meteor.destroy()


        for asteroid in asteroidGroup:
            if pygame.sprite.collide_mask(player, asteroid):
                player.explode()



        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()

        target_planet.update()
        planetGroup.update()
        planetGroup.draw(screen)
        asteroidGroup.update()
        asteroidGroup.draw(screen)
        wormholeGroup.update()
        wormholeGroup.draw(screen)
        meteorGroup.update()
        meteorGroup.draw(screen)
        blackholeGroup.update()
        blackholeGroup.draw(screen)
        shipGroup.update()
        shipGroup.draw(screen)
        player.update()

        if showintro:
            pygame.display.update()
            # offset(500, planetGroup, wormholeGroup, meteorGroup, blackholeGroup, asteroidGroup, target_planet, player)
            pygame.display.update()
            border = pygame.Rect((50, height - 185), (width - 100, 165))
            textbox = pygame.Rect((50, height - 185), (width - 100, 165))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext('TARS:', (60, 37))
            displayanimtext('Captain Cooper a massive asteroid of the size of the moon is expected to hit the earth within', (
                115, 37))
            displayanimtext('24 hours with a speed of 8 lakh Kmph that will wipe out life on earth. You are the most', (
                115, 38))
            displayanimtext('experienced intergalactic captain on the earth. So you are given the most important and', (115, 39))
            displayanimtext('dangerous task to take humans in the Endurance to Proxima Centauri B. It is almost 5', (115, 40))
            displayanimtext('light-years away, but our Ion thrusters have been upgraded. Due to the maximum ', (115, 41))
            displayanimtext('probability of life on Proxima Centauri B, we have previously sent many fleets of', (115, 42))
            displayanimtext('spaceships. The remaining spaceships will follow you. You can make history by escorting', (115, 43))
            displayanimtext('the whole human civilization to another planet that is never done before.', (115, 44))
            displayanimtext('Press ENTER to continue', (700, 45.5))
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            meteor_time = pygame.time.get_ticks()
                            if setting_music:
                                final_lvl_music.play(-1)

        if meteor_time:
            time_since_enter = pygame.time.get_ticks() - meteor_time
            if time_since_enter % 20000 > 15000:
                meteorWarning = True

            if time_since_enter / 20000 > timercount:
                timercount += 1
                thrust_on.stop()
                if setting_sound_effects:
                    global warning_effect
                    warning_effect.play()
                meteorWarning = False
                meteorWave = True
                meteors, meteorGroup = createmeteorWave(30,
                                                        player.rect.centerx)

        if meteorWarning:
            showMeteorWarning()
        if meteorWave:
            # displaytext("Meteor Shower", 30, screen.get_rect().centerx,
            #             screen.get_rect().centery, white)
            for m in meteors:
                m.update()
            if len(meteorGroup) == 0:
                meteorWave = False

        showfuelbar(player, [100, height - 20, player.fuel*(900/player.maxfuel), 10])

        if player.fuel <= 0:
            final_lvl_music.stop()
            player.gameOver = True
            gameovermenu = True
            game_over()

        if wormhole_travel1:
            if pygame.time.get_ticks() - start_time1 > 2000:
                wormhole_travel1 = False
                player.angle_speed = 0
            if player.vel.length() < 0.5:
                player.vel += player.acceleration

        if wormhole_travel2:
            if pygame.time.get_ticks() - start_time2 > 1000:
                wormhole_travel2 = False
                player.angle_speed = 0
            if player.vel.length() < 0.5:
                player.vel += player.acceleration

        if wormhole_travel3:
            if pygame.time.get_ticks() - start_time3 > 1000:
                wormhole_travel3 = False
                player.angle_speed = 0
            if player.vel.length() < 0.5:
                player.vel += player.acceleration

        pygame.display.flip()
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