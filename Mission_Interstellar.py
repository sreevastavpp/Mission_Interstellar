import math
import os
import random
from os import listdir
from os.path import isfile, join

import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

pygame.display.set_caption('Mission Intersteller')

size = (width, height) = (1024, 768)
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 155, 0)
red = (155, 0, 0)
blue = (0, 0, 155)
yellow = (255, 255, 0)
clock = pygame.time.Clock()

MAX_SPEED = 5
NORMAL_GRAVITY = 1.2
BLACK_HOLE_GRAVITY = 1.2

vec = pygame.math.Vector2

screen = pygame.display.set_mode(size, DOUBLEBUF | FULLSCREEN)

running = False
mainmenu = True
submenu = False
howtoplaymenu = False
settingsmenu = False
gameovermenu = False
lvlfinishmenu = False
gamefinishscreen = False
gameOver = False
setting_music = True
setting_sound_effects = True
currentLvl = 0

menu_select = pygame.mixer.Sound('Sprites/Sound Effects/button.wav')
menu_select.set_volume(0.3)
warning_effect = pygame.mixer.Sound('Sprites/Sound Effects/warning.wav')
warning_effect.set_volume(0.5)
intro_printing = pygame.mixer.Sound('Sprites/Sound Effects/intro_print.wav')
wormhole_effect = pygame.mixer.Sound(
    'Sprites/Sound Effects/wormhole_effect.wav')
meteor_effect = pygame.mixer.Sound('Sprites/Sound Effects/meteor.wav')
blackhole_effect = pygame.mixer.Sound('Sprites/Sound Effects/blackhole.wav')
blackhole_effect.set_volume(0.5)
thrust_on = pygame.mixer.Sound('Sprites/Sound Effects/rocket on.wav')
thrust_on.set_volume(0.1)
explosion_effect = pygame.mixer.Sound('Sprites/Sound Effects/explosion.wav')
explosion_effect.set_volume(0.5)
lvl_complete_effect = pygame.mixer.Sound(
    'Sprites/Sound Effects/lvl_complete.wav')
game_complete_effect = pygame.mixer.Sound(
    'Sprites/Sound Effects/game_complete.wav')
game_complete_effect.set_volume(0.5)
lvl_music = pygame.mixer.Sound('Sprites/Sound Effects/levelmusic1.wav')
lvl_music.set_volume(0.5)
final_lvl_music = pygame.mixer.Sound('Sprites/Sound Effects/levelmusic2.wav')
final_lvl_music.set_volume(0.5)
speed_vec = vec(0, 0)

desc_font = pygame.font.Font


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


def displaymenutext(
        text,
        fontsize,
        x,
        y,
        color,
):
    menufont = pygame.font.Font("Sprites/ethnocentric.otf", fontsize)
    text = menufont.render(text, 1, color)
    textpos = text.get_rect(centerx=x, centery=y)
    screen.blit(text, textpos)
    return text


def displaycustomanimtext(string, tuple, font, size, color, bgcolor=None):
    line_space = 16
    x, y = tuple
    y = y * line_space
    char = ''
    letter = 0
    count = 0
    for i in range(len(string)):
        basicfont = pygame.font.Font(font, size)
        pygame.event.clear()
        pygame.time.wait(25)
        char = char + string[letter]
        text = basicfont.render(char, False, color,
                                bgcolor)
        textrect = text.get_rect(
            topleft=(x,
                     y))
        screen.blit(text, textrect)
        pygame.display.update(
            textrect)
        count += 1
        letter += 1


def displayanimtext(string, tuple):
    line_space = 16
    x, y = tuple
    y = y * line_space
    char = ''
    letter = 0
    count = 0
    for i in range(len(string)):
        basicfont = pygame.font.Font("Sprites/s.ttf", 15)
        pygame.event.clear()
        pygame.time.wait(25)
        char = char + string[letter]
        text = basicfont.render(char, False, (2, 241,
                                              16))
        textrect = text.get_rect(
            topleft=(x,
                     y))
        screen.blit(text, textrect)
        pygame.display.update(
            textrect)
        count += 1
        letter += 1


class Button:
    def __init__(self, text, width, height, pos, elevation, pressed):
        self.font = pygame.font.Font("Sprites/ethnocentric.otf", 20)
        self.pressed = pressed
        self.top_rect = pygame.Rect(pos, (width, height))
        self.border = pygame.Rect(pos, (width + 2, height + 2))
        self.top_color = blue
        self.border_color = blue

        self.text = text
        self.text_surf = self.font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def change_text(self, newtext):
        self.text_surf = self.font.render(newtext, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def draw(self):
        if self.pressed:
            self.change_text("On")
            self.top_color = blue
        else:
            self.change_text("Off")
            self.top_color = black
        pygame.draw.rect(screen, self.top_color, self.top_rect,
                         border_radius=12)
        pygame.draw.rect(screen, self.border_color, self.border, 2,
                         border_radius=12)
        screen.blit(self.text_surf, self.text_rect)

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                if setting_sound_effects:
                    menu_select.play()
                if self.pressed:
                    self.pressed = False
                    self.change_text("Off")
                    self.top_color = black
                else:
                    self.pressed = True
                    self.change_text("On")
                    self.top_color = blue

        return self.pressed


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


def showfuelbar(player, pos):
    unit = 900 / player.maxfuel
    if player.fuel > 0:
        fuelbar = pygame.Surface((player.fuel * unit, 10), pygame.SRCALPHA, 32)
        fuelbar.convert_alpha()
        barcolor = green

        if player.fuel > player.maxfuel * 0.6:
            barcolor = green
        elif player.fuel > player.maxfuel * 0.3:
            barcolor = yellow
        elif player.fuel < player.maxfuel * 0.3 and player.fuel > 0:
            warning("Low Fuel!!!")
            barcolor = red

        rect = pygame.draw.rect(screen, barcolor, pos)
        displaymenutext('FUEL', 15, 60, height - 15, white)


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
            pygame.draw.circle(screen, self.color,
                               (self.starpos[x][0], self.starpos[x][1]),
                               self.radius)
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


def blackhole_collision(left, right):
    if left != right:
        return left.rect2.colliderect(right.rect)
    else:
        return False


def vicinity_collision(left, right):
    if left != right:
        return left.vicinity_rect.colliderect(right.rect)
    else:
        return False


class Planets(pygame.sprite.Sprite):

    def __init__(self, radius, pos, target=False, translate=False):
        pygame.sprite.Sprite.__init__(self)

        if target:
            files = [f for f in listdir("Sprites/Target Planets") if
                     isfile(join("Sprites/Target Planets", f))]

            file = files[random.randrange(0, len(files))]

            (self.image, self.rect) = load_image(join("Target Planets", file),
                                                 radius,
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
        self.translate = translate

    def update(self):
        if self.translate:
            self.pos -= speed_vec
            self.rect.center = self.pos
            self.vicinity_rect.center = self.rect.center

        screen.blit(self.image, self.rect)


class WormHole(pygame.sprite.Sprite):

    def __init__(self, pos, angle, radius, translate=False):
        pygame.sprite.Sprite.__init__(self)

        (self.original_image, self.rect) = load_image('wormhole.png', radius,
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


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, pos, radius, rot_radius, offset, sign, angle_speed,
                 *groups, translate=False):
        super().__init__(*groups)
        files = [f for f in listdir("Sprites/Asteroids") if
                 isfile(join("Sprites/Asteroids", f))]

        file = files[random.randrange(0, len(files))]

        (self.image, self.rect) = load_image(join("Asteroids", file), radius,
                                             radius, -1)

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

        (self.image, self.rect) = load_image('Meteors/meteor.png',
                                             radius * 0.7,
                                             2 * radius, -1)
        self.original_image = self.image
        self.angle = round(math.atan2(speed.x, speed.y) / math.pi * 180)
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pos = vec(pos)
        self.speed = speed
        self.explosion_sound = pygame.mixer.Sound('Sprites/Sound Effects/explosion.wav')
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

    def recenter(self):
        self.pos = self.initial_pos
        self.rect.center = self.pos

    def destroy(self):
        (x, y) = self.rect.center
        thrust_on.stop()
        if setting_sound_effects:
            self.explosion_sound.play(maxtime=1000)

        self.explosion = Explosion(x, y, 60)
        for i in range(0, 30):
            self.explosion.update()

        self.kill()
        self.explosion.kill()


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

        self.image = self.images[0]
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        screen.blit(self.image, self.rect)
        pygame.display.update()

    def update(self):
        self.image = self.images[self.index]
        screen.blit(self.image, self.rect)
        pygame.display.update()
        if self.index + 1 >= len(self.images):
            self.index = 0
        else:
            self.index += 1


class Ship(pygame.sprite.Sprite):

    def __init__(self, img, rect, pos, angle, rot_radius=0, offset=0, sign="-",
                 angle_speed=0, translate=False, rotate=False):
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = img, rect
        self.original_image = self.image
        if not angle == 0:
            self.image = pygame.transform.rotate(self.original_image, -angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = pos
        self.pos = vec(pos)
        self.translate = translate
        self.rotate = rotate
        self.sign = sign

        if self.sign == "-":
            self.offset = vec(-rot_radius, offset)
        else:
            self.offset = vec(rot_radius, offset)
        self.angle = 0
        self.angle_speed = angle_speed
        self.rect.center = pos

    def update(self):
        if self.translate:
            self.pos -= speed_vec
            self.rect.center = self.pos

        if self.rotate:
            if self.sign == "-":
                self.angle -= self.angle_speed
            else:
                self.angle += self.angle_speed
            self.rect.center = self.pos + self.offset.rotate(self.angle)

        screen.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):

    def __init__(self, pos, translate=False):
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
        self.throughWormhole = False
        self.explosion_sound = pygame.mixer.Sound('Sprites/Sound Effects/explosion.wav')
        self.explosion_sound.set_volume(0.1)
        self.flame_up = flame(40, 80, self, 1)
        self.flame_down = flame(40, 80, self, 4)
        self.flame_right = flame(40, 40, self, 3)
        self.flame_left = flame(40, 40, self, 2)
        self.rect.center = pos
        self.translate = translate

    def rotate(self):
        self.acceleration.rotate_ip(self.angle_speed)
        self.angle += self.angle_speed
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.throughWormhole:
            self.angle_speed = 0
            self.throughWormhole = False

    def checkbounds(self):
        global gameovermenu
        if not self.translate:
            if self.rect.left > width:
                lvl_music.stop()
                self.gameOver = True
                gameovermenu = True
                game_over()
            if self.rect.right < 0:
                lvl_music.stop()
                self.gameOver = True
                gameovermenu = True
                game_over()
            if self.rect.top > height:
                lvl_music.stop()
                self.gameOver = True
                gameovermenu = True
                game_over()
            if self.rect.bottom < 0:
                lvl_music.stop()
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
            if setting_sound_effects:
                thrust_on.play()
        if keys[K_RIGHT]:
            self.angle_speed = 1
            self.rotate()
            self.fuel -= 0.01
            self.flame_right.update(self)
            if setting_sound_effects:
                thrust_on.play()
        if keys[K_UP]:
            self.vel += self.acceleration
            self.fuel -= 0.05
            self.flame_up.update(self)
            if setting_sound_effects:
                thrust_on.play()

        if keys[K_DOWN]:
            self.vel -= self.acceleration
            self.fuel -= 0.05
            self.flame_down.update(self)
            if setting_sound_effects:
                thrust_on.play()
        if keys[K_SPACE]:
            brake_vector = vec(-(self.vel.x * 0.1), -(self.vel.y * 0.1))
            self.vel += brake_vector
            self.fuel -= 0.1
            self.flame_up.update(self)
            self.flame_down.update(self)
            self.flame_right.update(self)
            self.flame_left.update(self)
            if setting_sound_effects:
                thrust_on.play()
        if keys[K_ESCAPE]:
            lvl_music.stop()
            final_lvl_music.stop()
            self.gameOver = True
            global gameovermenu
            gameovermenu = True
            game_over()

        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        global speed_vec
        speed_vec = self.vel
        if self.translate:
            self.position += self.vel * 0.05
        else:
            self.position += self.vel

        self.rect.center = self.position

        screen.blit(self.image, self.rect)

    def explode(self, blackhole=False):
        (x, y) = self.rect.center
        lvl_music.stop()
        final_lvl_music.stop()
        if setting_sound_effects:
            if blackhole:
                thrust_on.stop()
                blackhole_effect.play()
            else:
                thrust_on.stop()
                explosion_effect.play(maxtime=1000)

        self.explosion = Explosion(x, y, 60)
        for i in range(0, 50):
            self.explosion.update()

        self.kill()
        self.explosion.kill()
        self.gameOver = True
        global gameovermenu
        gameovermenu = True
        game_over()

    def gravity(self, planet, gravity_const):
        gravity_const = gravity_const
        dx = self.position.x - planet.rect.centerx
        dy = self.position.y - planet.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance

        if planet.radius * 0.5 < distance < planet.radius * gravity_const:
            angle_btw = vec(self.rect.center).angle_to(planet.rect.center)
            planet_distance = (planet.radius * gravity_const - distance)

            if self.vel.magnitude() < 0.5:
                angle_constant = gravity_const * 10 * planet_distance
            else:
                angle_constant = gravity_const * 20 * self.vel.magnitude() * planet_distance

            if not 8 < abs(angle_btw) < 10:
                if planet.rect.left - self.rect.x > planet.rect.right - self.rect.x:
                    if 230 < self.angle or self.angle < 60:
                        self.angle_speed = (
                                                   angle_btw * angle_constant) / planet.radius
                    else:
                        self.angle_speed = -(
                                angle_btw * angle_constant) / planet.radius
                else:
                    if 230 < self.angle or self.angle < 60:
                        self.angle_speed = -(
                                angle_btw * gravity_const * self.vel.magnitude() * 2) / planet.radius
                    else:
                        self.angle_speed = (
                                                   angle_btw * gravity_const * self.vel.magnitude() * 2) / planet.radius

            self.vel -= vec(dx, dy) * 0.02

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
            (self.image, self.rect) = load_image('flame_up.png', width, length,
                                                 -1)
        elif direction == 2:
            (self.image, self.rect) = load_image('flame_right.png', width,
                                                 length, -1)
        elif direction == 3:
            (self.image, self.rect) = load_image('flame_left.png', width,
                                                 length, -1)
        elif direction == 4:
            (self.image, self.rect) = load_image('flame_down.png', width,
                                                 length, -1)

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


def main_menu():
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    global gamefinishscreen
    global mainmenu
    global submenu
    global settingsmenu
    global howtoplaymenu
    global running
    global speed_vec
    selected = 0
    color1 = white
    color2 = yellow
    color3 = yellow
    color4 = yellow

    while mainmenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if setting_sound_effects:
                        menu_select.play()
                    selected -= 1
                elif event.key == pygame.K_DOWN:
                    if setting_sound_effects:
                        menu_select.play()
                    selected += 1

                if event.key == pygame.K_RETURN:
                    if setting_sound_effects:
                        menu_select.play()
                    if selected == 0:
                        mainmenu = False
                        submenu = True
                        # gamefinishscreen = True
                        # game_finished()
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
        starfield1.drawstars()
        starfield2.drawstars()
        if selected > 3:
            selected = 0
        if selected < 0:
            selected = 3

        if (selected == 0):
            color1 = white
            color2 = yellow
            color3 = yellow
            color4 = yellow
        elif (selected == 1):
            color1 = yellow
            color2 = white
            color3 = yellow
            color4 = yellow
        elif (selected == 2):
            color1 = yellow
            color2 = yellow
            color3 = white
            color4 = yellow
        elif (selected == 3):
            color1 = yellow
            color2 = yellow
            color3 = yellow
            color4 = white

        main_img, main_rect = load_image("mission-interstellar.png", 800,
                                         400, -1)
        main_rect.center = (screen.get_width() / 2, 200)
        screen.blit(main_img, main_rect)

        displaymenutext('Play', 25, width / 2 - 20, height - 300, color1)
        displaymenutext('Options', 25, width / 2 - 20, height - 225, color2)
        displaymenutext('How To Play', 25, width / 2 - 20, height - 150,
                        color3)
        displaymenutext('Exit', 25, width / 2 - 20, height - 75, color4)

        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 20,
                    white)

        speed_vec = vec(0, -1)
        pygame.display.update()
        clock.tick(60)


def buttons_draw(buttons):
    for b in buttons:
        b.draw()


def settings():
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)
    buttons = []
    global mainmenu
    global settingsmenu
    global setting_music
    global setting_sound_effects
    global speed_vec

    button1 = Button('On', 100, 40, (width / 2 + 50, height - 420), 5,
                     setting_music)
    button2 = Button('On', 100, 40, (width / 2 + 50, height - 320), 5,
                     setting_sound_effects)
    buttons.append(button1)
    buttons.append(button2)

    while settingsmenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainmenu = True
                settingsmenu = False
                main_menu()
            if event.type == pygame.KEYDOWN:
                if setting_sound_effects:
                    menu_select.play()
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    mainmenu = True
                    settingsmenu = False
                    main_menu()

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()
        displaymenutext('Music', 20, width / 2 - 90, height - 400, white)
        displaymenutext('Sound Effects', 20, width / 2 - 90, height - 300,
                        white)

        displaymenutext('Use Mouse for selection', 15, width / 2, height - 100,
                        white)

        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 20,
                    white)

        speed_vec = vec(0, -1)

        setting_music = button1.check_click()
        setting_sound_effects = button2.check_click()

        buttons_draw(buttons)
        pygame.display.update()
        clock.tick(5)


def howtoplay():
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)

    global mainmenu
    global howtoplaymenu
    global speed_vec
    speed_vec = vec(0, -1)

    scroll_up = True
    scroll_down = True

    window_offset = 0

    while howtoplaymenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainmenu = True
                howtoplaymenu = False
                main_menu()

        keys = pygame.key.get_pressed()
        if scroll_down:
            if keys[K_UP]:
                window_offset -= 5
                speed_vec += vec(0, -0.04)
        if scroll_up:
            if keys[K_DOWN]:
                window_offset += 5
                speed_vec -= vec(0, -0.04)
        if keys[K_ESCAPE] or keys[K_BACKSPACE]:
            mainmenu = True
            howtoplaymenu = False
            main_menu()

        screen.fill((0, 0, 0))

        starfield1.drawstars()
        starfield2.drawstars()

        ship, ship_rect = load_image("ship.png", 100, 100, -1)
        ship_rect.center = (100, 150)
        ship_rect.centery += window_offset
        screen.blit(ship, ship_rect)

        planet, planet_rect = load_image("Planets/planet2.png", 100, 100, -1)
        planet_rect.center = (100, 400)
        planet_rect.centery += window_offset
        screen.blit(planet, planet_rect)

        asteroid, asteroid_rect = load_image("Asteroids/asteroid.png", 100,
                                             100, -1)
        asteroid_rect.center = (100, 650)
        asteroid_rect.centery += window_offset
        screen.blit(asteroid, asteroid_rect)

        meteor, meteor_rect = load_image("Meteors/meteor.png", 50, 100, -1)
        meteor_rect.center = (100, 900)
        meteor_rect.centery += window_offset
        screen.blit(meteor, meteor_rect)

        blackhole, blackhole_rect = load_image("blackhole.png", 200,
                                               (150 * 0.6), -1)
        blackhole_rect.center = (100, 1150)
        blackhole_rect.centery += window_offset
        screen.blit(blackhole, blackhole_rect)

        wormhole, wormhole_rect = load_image("wormhole.png", 150, (150 * 0.65),
                                             -1)
        wormhole_rect.center = (100, 1400)
        wormhole_rect.centery += window_offset
        screen.blit(wormhole, wormhole_rect)

        displaymenutext('Player Spaceship', 25, screen.get_width() / 2,
                        ship_rect.top - 50, white)
        displaytext(
            'Use Arrows keys for the movement and SPACE key for the brakes',
            24, screen.get_width() / 2,
                ship_rect.top + 30, yellow)
        displaytext(
            'Turning requires minimum fuel while brakes require maximum fuel.',
            24, screen.get_width() / 2,
                ship_rect.top + 60, yellow)
        displaytext('If the fuel of Spaceship gets empty, the player is out.', 24,
                    screen.get_width() / 2,
                    ship_rect.top + 90, yellow)

        displaymenutext('Planets', 25, screen.get_width() / 2,
                        planet_rect.top - 50, white)
        displaytext(
            'Planets vary in different radius and surface types and all planets possess ',
            24, screen.get_width() / 2,
                planet_rect.top + 30, yellow)
        displaytext(
            'gravitational power that can pull and destroy the spaceship. But this gravity',
            24, screen.get_width() / 2,
                planet_rect.top + 60, yellow)
        displaytext('can also be used to propel the spaceship.', 24,
                    screen.get_width() / 2,
                    planet_rect.top + 90, yellow)

        displaymenutext('Asteroids', 25, screen.get_width() / 2,
                        asteroid_rect.top - 50, white)
        displaytext(
            'Asteroids revolve around planets and blackholes. Asteroids vary',
            24, screen.get_width() / 2, asteroid_rect.top + 30, yellow)
        displaytext(
            'in different radius, surface types and speed of revolution but asteroids can',
            24, screen.get_width() / 2, asteroid_rect.top + 60, yellow)
        displaytext(
            ' destroy the spaceship on collision. So avoid going near them.',
            24, screen.get_width() / 2, asteroid_rect.top + 90, yellow)

        displaymenutext('Meteors', 25, screen.get_width() / 2,
                        meteor_rect.top - 50, white)
        displaytext(
            'Meteors travel in group in the space. Meteors vary in different shape, sizes,',
            24, screen.get_width() / 2, meteor_rect.top + 30, yellow)
        displaytext(
            'speed and trails. An alert occurs 5 secs before the meteors shower. Meteors can',
            24, screen.get_width() / 2, meteor_rect.top + 60, yellow)
        displaytext(
            'destroy the spaceship on collision. Asteroids can help against meteors.',
            24, screen.get_width() / 2, meteor_rect.top + 90,
            yellow)

        displaymenutext('Black Hole', 25, screen.get_width() / 2,
                        blackhole_rect.top - 50, white)
        displaytext(
            'Black Hole is a region in the space with very strong gravity.',
            24, screen.get_width() / 2, blackhole_rect.top + 20, yellow)
        displaytext(
            'Blackholes have big radius of gravity and can pull the spaceship ',
            24, screen.get_width() / 2, blackhole_rect.top + 50, yellow)
        displaytext(
            'from large distance. Once pulled in, spaceship cannot',
            24, screen.get_width() / 2, blackhole_rect.top + 80,
            yellow)
        displaytext(
            'escape from blackhole.',
            24, screen.get_width() / 2, blackhole_rect.top + 110,
            yellow)

        displaymenutext('Worm Hole', 25, screen.get_width() / 2,
                        wormhole_rect.top - 50, white)
        displaytext(
            'Worm hole resembles a tunnel between two points in space-time.',
            24, screen.get_width() / 2, wormhole_rect.top + 30, yellow)
        displaytext(
            'It provides a shortcut by shorter path. It can be used to reach',
            24, screen.get_width() / 2, wormhole_rect.top + 60, yellow)
        displaytext(
            'some other point in space without using fuel.',
            24, screen.get_width() / 2, wormhole_rect.top + 90,
            yellow)

        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 20,
                    white)

        if screen.get_height() - wormhole_rect.bottom > 50:
            scroll_down = False
        else:
            scroll_down = True

        if ship_rect.top > 100:
            scroll_up = False
        else:
            scroll_up = True

        pygame.display.update()
        clock.tick(120)


def level_menu():
    color1 = yellow
    # color2 = yellow
    # color3 = yellow
    # color4 = yellow
    # color5 = yellow

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
                    if setting_sound_effects:
                        menu_select.play()
                    selected -= 1
                elif event.key == pygame.K_DOWN:
                    if setting_sound_effects:
                        menu_select.play()
                    selected += 1
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    if setting_sound_effects:
                        menu_select.play()
                    mainmenu = True
                    submenu = False
                    main_menu()

                if event.key == pygame.K_RETURN:
                    if setting_sound_effects:
                        menu_select.play()
                    submenu = False
                    running = True
                    currentLvl = selected
                    if selected == 0:
                        level_1()
                    # if selected == 1:
                    #     level_2()
                    # if selected == 2:
                    #     level_3()
                    # if selected == 3:
                    #     level_4()
                    # if selected == 4:
                    #     level_5()

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()
        if selected > 1:
            selected = 0
        if selected < 0:
            selected = 0

        if (selected == 0):
            color1 = white
            # color2 = yellow
            # color3 = yellow
            # color4 = yellow
            # color5 = yellow
        # elif (selected == 1):
        #     color1 = yellow
        #     color2 = white
        #     color3 = yellow
        #     color4 = yellow
        #     color5 = yellow
        # elif (selected == 2):
        #     color1 = yellow
        #     color2 = yellow
        #     color3 = white
        #     color4 = yellow
        #     color5 = yellow
        # elif (selected == 3):
        #     color1 = yellow
        #     color2 = yellow
        #     color3 = yellow
        #     color4 = white
        #     color5 = yellow
        # elif (selected == 4):
        #     color1 = yellow
        #     color2 = yellow
        #     color3 = yellow
        #     color4 = yellow
        #     color5 = white

        main_img, main_rect = load_image("mission-interstellar.png", 800,
                                         400, -1)
        main_rect.center = (screen.get_width() / 2, 200)
        screen.blit(main_img, main_rect)

        displaymenutext('Level 1', 25, width / 2 - 20, height - 350, color1)
        # displaymenutext('Level 2', 25, width / 2 - 20, height - 275, color2)
        # displaymenutext('Level 3', 25, width / 2 - 20, height - 200, color3)
        # displaymenutext('Level 4', 25, width / 2 - 20, height - 125, color4)
        # displaymenutext('Level 5', 25, width / 2 - 20, height - 50, color5)

        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 20,
                    white)

        speed_vec = vec(0, -1)
        pygame.display.update()
        clock.tick(60)


def level_1():
    global running
    global gameovermenu
    global lvlfinishmenu
    global speed_vec

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
    target_planet = Planets(100, (900, 500), True)

    planetGroup.add(planet2)
    planetGroup.add(planet3)
    planetGroup.add(planet4)
    planetGroup.add(planet5)

    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)

    while running and not player.gameOver:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                lvl_music.stop()
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
                lvl_music.stop()
                thrust_on.stop()
                if setting_sound_effects:
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
            border = pygame.Rect((50, height - 120), (width - 100, 90))
            textbox = pygame.Rect((50, height - 120), (width - 100, 90))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)

            displayanimtext('TARS:', (60, 41))
            displayanimtext(
                'Hello Captain Cooper. Earth is no more habitable, so you are directed to take the Endurance',
                (
                    110, 41))
            displayanimtext(
                'ship with 1000 frozen human embryos and reach the planet, Pandora. Our previous teams have',
                (110, 42))
            displayanimtext(
                'landed there. You might find their spaceship. Are you ready to save humanity? ',
                (110, 43))
            displayanimtext('Press ENTER to continue', (700, 44.5))
            arrow_img, arrow_rect = load_image("arrow.png", 20, 20, -1)
            arrow_rect.center = (
                target_planet.rect.centerx, target_planet.rect.centery + 60)
            screen.blit(arrow_img, arrow_rect)
            pygame.display.update()
            displaycustomanimtext('Target Planet',
                                  (target_planet.pos.x - 80, 36),
                                  "Sprites/ethnocentric.otf", 15, yellow)
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            if setting_music:
                                lvl_music.play(-1)

        showfuelbar(player,
                    [100, height - 20, player.fuel * (900 / player.maxfuel),
                     10])

        if player.fuel <= 0:
            lvl_music.stop()
            player.gameOver = True
            gameovermenu = True
            game_over()

        pygame.display.flip()
        clock.tick(60)


def createmeteorWave(num, posx):
    meteors = []
    mtg = pygame.sprite.Group()
    for i in range(num):
        randx = random.randrange(posx - 300, posx + 200)
        randy = random.randrange(0, 100) - 50
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

    planet2 = Planets(200, (250, 600))
    planet3 = Planets(150, (650, 200))
    planet4 = Planets(100, (250, 100))
    planet5 = Planets(125, (600, 700))
    target_planet = Planets(150, (900, 500), True)

    planetGroup.add(planet2)
    planetGroup.add(planet3)
    planetGroup.add(planet4)
    planetGroup.add(planet5)

    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)

    asteroidGroup = pygame.sprite.Group()
    Asteroid(planet4.pos, 20, 90, 10, "-", 1.5, asteroidGroup)
    Asteroid(planet4.pos, 25, 100, -50, "+", 1, asteroidGroup)
    Asteroid(planet4.pos, 30, 105, 90, "-", 0.8, asteroidGroup)

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
                lvl_music.stop()
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
                lvl_music.stop()
                thrust_on.stop()
                if setting_sound_effects:
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

        target_planet.update()
        planetGroup.update()
        planetGroup.draw(screen)
        asteroidGroup.update()
        asteroidGroup.draw(screen)
        player.update()

        if showintro:
            pygame.display.update()
            border = pygame.Rect((50, height - 120), (width - 100, 100))
            textbox = pygame.Rect((50, height - 120), (width - 100, 100))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext('TARS:', (60, 41))
            displayanimtext(
                'Heyy Captain Cooper it seems you are ready for the next mission. Your next mission is to land',
                (
                    110, 41))
            displayanimtext(
                'on the Krypton planet. Due to the asteroids and meteors, our previous team crashed before',
                (110, 42))
            displayanimtext(
                'reaching there. If you find the planet habitable drop the rover, and base station and send',
                (110, 43))
            displayanimtext('SOS signal. Keep the hope alive.', (110, 44))
            displayanimtext('Press ENTER to continue', (700, 45.5))
            arrow_img, arrow_rect = load_image("arrow.png", 20, 20, -1)
            arrow_rect.center = (
                target_planet.rect.centerx, target_planet.rect.centery + 85)
            screen.blit(arrow_img, arrow_rect)
            pygame.display.update()
            displaycustomanimtext('Target Planet',
                                  (target_planet.pos.x - 80, 37.5),
                                  "Sprites/ethnocentric.otf", 15, yellow)
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            start_time = pygame.time.get_ticks()
                            if setting_music:
                                lvl_music.play(-1)

        if start_time:
            time_since_enter = pygame.time.get_ticks() - start_time
            if time_since_enter % 20000 > 15000:
                meteorWarning = True

            if time_since_enter / 20000 > timercount:
                timercount += 1
                meteorWarning = False
                meteorWave = True
                if setting_sound_effects:
                    global warning_effect
                    warning_effect.play()
                meteors, meteorGroup = createmeteorWave(15,
                                                        player.rect.centerx)

        if player.fuel <= 0:
            lvl_music.stop()
            player.gameOver = True
            gameovermenu = True
            game_over()

        showfuelbar(player,
                    [100, height - 20, player.fuel * (900 / player.maxfuel),
                     10])

        if meteorWarning:
            showMeteorWarning()
        if meteorWave:
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

    planet2 = Planets(200, (100, 600))
    planet3 = Planets(250, (600, 700))
    planet4 = Planets(100, (300, 100))
    planet5 = Planets(125, (750, 250))
    target_planet = Planets(100, (900, 500), True)

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
                lvl_music.stop()
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
                lvl_music.stop()
                thrust_on.stop()
                if setting_sound_effects:
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

        if pygame.sprite.collide_mask(player, blackhole):
            player.explode(True)

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()

        planet2.update()
        planet3.update()
        planet4.update()
        planet5.update()
        target_planet.update()
        blackhole.update()
        player.update()

        if showintro:
            pygame.display.update()
            border = pygame.Rect((50, height - 135), (width - 100, 115))
            textbox = pygame.Rect((50, height - 135), (width - 100, 115))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext('TARS:', (60, 40))
            displayanimtext(
                'Good to see you, Captain Cooper. Since you are so experienced a critical mission has been',
                (115, 40))
            displayanimtext(
                'assigned to you that no one has endeavoured. There is a Cybertron planet on the far end',
                (115, 41))
            displayanimtext(
                'of our galaxy. It is believed that intelligent species exist on Cybertron. Try to',
                (115, 42))
            displayanimtext(
                'communicate with them to help humans. You will also encounter a massive Blackhole',
                (115, 43))
            displayanimtext(
                'in the path, the biggest in the milky way. Avoid going near it.',
                (115, 44))
            displayanimtext('Press ENTER to continue', (700, 45))
            arrow_img, arrow_rect = load_image("arrow.png", 20, 20, -1)
            arrow_rect.center = (
                target_planet.rect.centerx, target_planet.rect.centery + 60)
            screen.blit(arrow_img, arrow_rect)
            pygame.display.update()
            displaycustomanimtext('Target Planet',
                                  (target_planet.pos.x - 80, 36),
                                  "Sprites/ethnocentric.otf", 15, yellow)
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            if setting_music:
                                lvl_music.play(-1)

        showfuelbar(player,
                    [100, height - 20, player.fuel * (900 / player.maxfuel),
                     10])

        if player.fuel <= 0:
            lvl_music.stop()
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
                lvl_music.stop()
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
                lvl_music.stop()
                thrust_on.stop()
                if setting_sound_effects:
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
            border = pygame.Rect((50, height - 135), (width - 90, 115))
            textbox = pygame.Rect((50, height - 135), (width - 90, 115))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext('TARS:', (60, 40))
            displayanimtext(
                'Captain Cooper, there is bad news. The fuel tank was damaged by the black hole and a large',
                (
                    115, 40))
            displayanimtext(
                'amount of fuel leaked. We need to head towards Solaris about 2 lightyears away. We cannot',
                (
                    115, 41))
            displayanimtext(
                'reach Solaris with low fuel, so I found a wormhole in the path that can shorten our journey.',
                (115, 42))
            displayanimtext(
                'Our previous team almost reached Solaris but was pulled due to the strong magnetic fields',
                (115, 43))
            displayanimtext(
                'fields at the other end of the wormhole, so be careful. Hoping to reach without collision.',
                (115, 44))
            displayanimtext('Press ENTER to continue', (700, 45.5))
            arrow_img, arrow_rect = load_image("arrow.png", 20, 20, -1)
            arrow_rect.center = (
                target_planet.rect.centerx, target_planet.rect.centery + 85)
            screen.blit(arrow_img, arrow_rect)
            pygame.display.update()
            displaycustomanimtext('Target Planet',
                                  (target_planet.pos.x - 80, 37.5),
                                  "Sprites/ethnocentric.otf", 15, yellow)
            intro_printing.stop()

            while showintro:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            showintro = False
                            meteor_time = pygame.time.get_ticks()
                            if setting_music:
                                lvl_music.play(-1)

        if meteor_time:
            time_since_enter = pygame.time.get_ticks() - meteor_time
            if time_since_enter % 20000 > 15000:
                meteorWarning = True

            if time_since_enter / 20000 > timercount:
                timercount += 1
                meteorWarning = False
                meteorWave = True
                if setting_sound_effects:
                    global warning_effect
                    warning_effect.play()
                meteors, meteorGroup = createmeteorWave(15,
                                                        player.rect.centerx)

        if meteorWarning:
            showMeteorWarning()
        if meteorWave:
            for m in meteors:
                m.update()
            if len(meteorGroup) == 0:
                meteorWave = False

        showfuelbar(player,
                    [100, height - 20, player.fuel * (900 / player.maxfuel),
                     10])

        if player.fuel <= 0:
            lvl_music.stop()
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


def offset(offset, planetGroup, wormholeGroup, meteorGroup, blackholeGroup,
           asteroidGroup, target_pt, shipGroup, player, withplayer=False):
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
    player.fuel = 100
    player.maxfuel = 100
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

    image, rect = load_image(join("Spaceship", files[2]), 70,
                             35, -1)
    ship = Ship(image, rect, (4600, 500), -40, 200, translate=True)
    shipGroup.add(ship)

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
    ship = Ship(image, rect, (5200, 200), 0, 200, translate=True)
    shipGroup.add(ship)

    image, rect = load_image(join("Spaceship", files[7]), 50,
                             37, -1)
    ship = Ship(image, rect, target_planet.pos, 0, 170, -100, "-", 0.1,
                translate=True, rotate=True)
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
                offset(wormhole1.rect.centerx - wormhole2.rect.centerx,
                       planetGroup, wormholeGroup, meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup,
                       player)
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
                offset(wormhole2.rect.centerx - wormhole1.rect.centerx,
                       planetGroup, wormholeGroup, meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup,
                       player)
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
                offset(wormhole4.rect.left - wormhole3.rect.centerx,
                       planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup,
                       player)
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
                offset(wormhole3.rect.centerx - wormhole4.rect.centerx,
                       planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup,
                       player)
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
                offset(wormhole6.rect.centerx - wormhole5.rect.centerx + 50,
                       planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup,
                       player)
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
                offset(wormhole5.rect.centerx - wormhole6.rect.centerx,
                       planetGroup, wormholeGroup,
                       meteorGroup,
                       blackholeGroup, asteroidGroup, target_planet, shipGroup,
                       player)
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

        meteor_collided = pygame.sprite.groupcollide(meteorGroup,
                                                     blackholeGroup,
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

            screen.fill((0, 0, 0))
            starfield1.drawstars()
            starfield2.drawstars()
            offset(4500,
                   planetGroup, wormholeGroup, meteorGroup,
                   blackholeGroup, asteroidGroup, target_planet, shipGroup,
                   player, True)

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
            pygame.display.update()
            arrow_img, arrow_rect = load_image("arrow.png", 20, 20, -1)
            arrow_img = pygame.transform.rotate(arrow_img, 180)
            arrow_rect = arrow_img.get_rect(center=arrow_rect.center)
            arrow_rect.center = (695, 340)
            screen.blit(arrow_img, arrow_rect)
            displaycustomanimtext('Target Planet',
                                  (target_planet.pos.x - 90, 19),
                                  "Sprites/ethnocentric.otf", 15, yellow)
            pygame.display.update()
            pygame.time.wait(1000)

            border = pygame.Rect((50, height - 185), (width - 100, 165))
            textbox = pygame.Rect((50, height - 185), (width - 100, 165))
            pygame.draw.rect(screen, black, textbox, border_radius=12)
            pygame.draw.rect(screen, green, border, 2, border_radius=12)
            pygame.display.update()

            if setting_sound_effects:
                intro_printing.play(-1)
            displayanimtext('TARS:', (60, 37))
            displayanimtext(
                'Captain Cooper a massive asteroid of the size of the moon is expected to hit the earth within',
                (
                    115, 37))
            displayanimtext(
                '24 hours with a speed of 8 lakh Kmph that will wipe out life on earth. You are the most',
                (
                    115, 38))
            displayanimtext(
                'experienced intergalactic captain on the earth. So you are given the most important and',
                (115, 39))
            displayanimtext(
                'dangerous task to take humans in the Endurance to Proxima Centauri B. It is almost 5',
                (115, 40))
            displayanimtext(
                'light-years away, but our Ion thrusters have been upgraded. Due to the maximum ',
                (115, 41))
            displayanimtext(
                'probability of life on Proxima Centauri B, we have previously sent many fleets of',
                (115, 42))
            displayanimtext(
                'spaceships. The remaining spaceships will follow you. You can make history by escorting',
                (115, 43))
            displayanimtext(
                'the whole human civilization to another planet that is never done before.',
                (115, 44))
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
                                offset(-4500,
                                       planetGroup, wormholeGroup, meteorGroup,
                                       blackholeGroup, asteroidGroup,
                                       target_planet, shipGroup,
                                       player, True)

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
            for m in meteors:
                m.update()
            if len(meteorGroup) == 0:
                meteorWave = False

        showfuelbar(player,
                    [100, height - 20, player.fuel * (900 / player.maxfuel),
                     10])

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
    color1 = white
    color2 = yellow

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
                    if setting_sound_effects:
                        menu_select.play()
                    selected -= 1
                elif event.key == pygame.K_RIGHT:
                    if setting_sound_effects:
                        menu_select.play()
                    selected += 1
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    if setting_sound_effects:
                        menu_select.play()
                    mainmenu = True
                    gameovermenu = False
                    main_menu()

                if event.key == pygame.K_RETURN:
                    if setting_sound_effects:
                        menu_select.play()
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
        starfield1.drawstars()
        starfield2.drawstars()
        if selected > 1:
            selected = 0
        if selected < 0:
            selected = 1

        if (selected == 0):
            color1 = white
            color2 = yellow
        elif (selected == 1):
            color1 = yellow
            color2 = white

        displaymenutext('Game Over', 40, width / 2, 100, yellow)
        displaymenutext('Play Again', 25, width / 3 - 20, height - 400, color1)
        displaymenutext('Main Menu', 25, 2 * width / 3 + 20, height - 400,
                        color2)
        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 40,
                    white)

        speed_vec = vec(0, -1)
        pygame.display.update()
        clock.tick(60)


def lvl_finished():
    color1 = white
    color2 = yellow

    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)

    global mainmenu
    global running
    global speed_vec
    global currentLvl
    global lvlfinishmenu
    global gamefinishscreen
    selected = 0

    lvlfinishmenu = False
    gamefinishscreen = True
    game_finished()

    while lvlfinishmenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if setting_sound_effects:
                        menu_select.play()
                    selected -= 1
                elif event.key == pygame.K_RIGHT:
                    if setting_sound_effects:
                        menu_select.play()
                    selected += 1
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    if setting_sound_effects:
                        menu_select.play()
                    mainmenu = True
                    lvlfinishmenu = False
                    main_menu()

                if event.key == pygame.K_RETURN:
                    if setting_sound_effects:
                        menu_select.play()
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
        starfield1.drawstars()
        starfield2.drawstars()

        if (currentLvl == 4):
            lvlfinishmenu = False
            gamefinishscreen = True
            game_finished()

        if selected > 1:
            selected = 0
        if selected < 0:
            selected = 1

        if (selected == 0):
            color1 = white
            color2 = yellow
        elif (selected == 1):
            color1 = yellow
            color2 = white

        displaymenutext('Level Complete', 40, width / 2, 100, yellow)
        displaymenutext('Next Level', 25, width / 3 - 20, height - 400, color1)
        displaymenutext('Main Menu', 25, 2 * width / 3 + 20, height - 400,
                        color2)
        displaytext('Mission Intersteller 1.0', 12, width - 80, height - 40,
                    white)

        speed_vec = vec(0, -1)
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


def warning(text):
    displaymenutext(text, 35
                    , width / 2, height / 2, red)


def showMeteorWarning():
    displaymenutext("Meteor Wave Arriving", 20, screen.get_rect().centerx, 75,
                    red)


def game_finished():
    starfield1 = stars(1, (150, 150, 150), 75, 0.5)
    starfield2 = stars(1, (75, 75, 75), 200, 1)

    global mainmenu
    global speed_vec
    global gamefinishscreen
    show_finish_desc = True
    show_final_message = False

    while gamefinishscreen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainmenu = True
                gamefinishscreen = False
                main_menu()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE or event.key == pygame.K_RETURN:
                    if setting_sound_effects:
                        menu_select.play()
                    mainmenu = True
                    gamefinishscreen = False
                    main_menu()

        screen.fill((0, 0, 0))
        starfield1.drawstars()
        starfield2.drawstars()

        if show_finish_desc:
            img, rect = load_image("planet_landed.jpg", screen.get_width(),
                                   screen.get_height(), -1)
            rect.center = screen.get_rect().center
            rect.bottom = screen.get_rect().bottom
            screen.blit(img, rect)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displaycustomanimtext("Congratulations", (width / 2 - 200, 5),
                                  "Sprites/ethnocentric.otf", 30, yellow)
            displaycustomanimtext(
                "You have successfully completed this game and saved humanity by",
                (100, 20), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "rehabilitating humans on Proxima Centauri B. We will lead the ",
                (130, 21.5), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "mission to Pandora, Krypton, Cybertron and Solaris from the",
                (130, 23), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "Proxima Centauri base station. For now, rest as you have come",
                (120, 24.5), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext("a long way.", (width / 2 - 50, 26),
                                  "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext("Press Enter", (width / 2 - 80, 33),
                                  "Sprites/ethnocentric.otf", 20, white)

            displaytext('Mission Intersteller 1.0', 12, width - 80,
                        height - 40,
                        white)
            
            pygame.display.update()

            intro_printing.stop()

            while show_finish_desc:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            if setting_sound_effects:
                                menu_select.play()
                            show_finish_desc = False
                            show_final_message = True

        if show_final_message:
            timercount = 0
            screen.fill((0, 0, 0))
            pygame.display.update()
            img, rect = load_image("future.jpg", screen.get_width(),
                                   screen.get_height(), -1)
            rect.center = screen.get_rect().center
            rect.bottom = screen.get_rect().bottom
            print(screen.get_width())
            print(screen.get_height())
            screen.blit(img, rect)
            pygame.display.update()
            if setting_sound_effects:
                intro_printing.play(-1)
            displaycustomanimtext("Message from future gen", (200, 5),
                                  "Sprites/ethnocentric.otf", 30, yellow)
            displaycustomanimtext(
                "This game is based on fiction and hoping that you enjoyed playing it.",
                (100, 15), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "But the reason for developing this game is to bring awareness,",
                (80, 16.5), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "This fiction is slowly turning into reality on",
                (100, 18), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "Earth. With every passing day, thousands of trees are being cut down,",
                (90, 19.5), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "numerous animal species are going extinct, water, land and air are",
                (100, 21), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "polluted, and there are numerous more human activities poisoning",
                (100, 22.5), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "the environment. Do you see your future as an intelligent civilized",
                (100, 24), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext("interplanetary species on this path?",
                                  (300, 25.5), "Sprites/ethnocentric.otf", 15,
                                  white)

            displaycustomanimtext(
                "Definitely No. Please help restore Mother Nature, your own home. Your",
                (100, 29), "Sprites/ethnocentric.otf", 15, white)
            displaycustomanimtext(
                "small contribution can turn the fate of the whole planet collaboratively.",
                (70, 30.5), "Sprites/ethnocentric.otf", 15, white)

            displaycustomanimtext(
                "Follow the Reduce, Reuse, Recycle and Restore principle",
                (80, 35), "Sprites/ethnocentric.otf", 20, yellow)
            displaytext('Mission Intersteller 1.0', 12, width - 80,
                        height - 40,
                        white)
            slide_time = pygame.time.get_ticks()
            pygame.display.update()

            intro_printing.stop()

            while show_final_message:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            if setting_sound_effects:
                                menu_select.play()
                            show_final_message = False
                            mainmenu = True
                            gamefinishscreen = False
                            main_menu()

                time_since_enter = pygame.time.get_ticks() - slide_time
                if time_since_enter / 1000 > timercount:
                    timercount += 1

            displaytext('Mission Intersteller 1.0', 12, width - 80,
                        height - 40,
                        white)
            pygame.display.update()

        speed_vec = vec(0, -1)
        pygame.display.update()
        clock.tick(60)


main_menu()
