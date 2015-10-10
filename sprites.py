"""
AsteroidImpact game sprites including sprite-specific behaviors.
"""
import pygame
from resources import load_image, load_sound
import virtualdisplay
import math

class VirtualGameSprite(pygame.sprite.Sprite):
    """
    Sprite with higher resolution game position/size (gamerect) than on-screen
    position/size (rect)
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.gamerect = pygame.Rect(0, 0, 1, 1)
    def update_rect(self):
        self.rect = virtualdisplay.screenrect_from_gamerect(self.gamerect)

#classes for our game objects
class Cursor(VirtualGameSprite):
    def __init__(self):
        VirtualGameSprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('cursor.png', -1)
        self.image = self.image.convert_alpha()
        self.gamediameter = 32
        # find screen diameter
        self.gamerect = pygame.Rect(0, 0, self.gamediameter,self.gamediameter)
        self.update_rect()
        self.image = pygame.transform.smoothscale(
            self.image,
            (self.rect.width, self.rect.height))
        self.image.convert()

    def update(self, millis):
        "move the cursor based on the mouse position"
        pos = pygame.mouse.get_pos()

        # if the cursor is outside of the game area, move it back
        if not virtualdisplay.screenarea.collidepoint(pos):
            pos = (
                max(
                    min(pos[0], virtualdisplay.screenarea.right),
                    virtualdisplay.screenarea.left),
                max(
                    min(pos[1], virtualdisplay.screenarea.bottom),
                    virtualdisplay.screenarea.top))
            pygame.mouse.set_pos(pos)

        game_pos = virtualdisplay.gamepoint_from_screenpoint(pos)
        self.gamerect.center = game_pos
        self.update_rect()


class Target(VirtualGameSprite):
    def __init__(self, diameter=32, left=20, top=20):
        VirtualGameSprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('crystal.png', -1)
        self.image = self.image.convert_alpha()
        self.gamediameter = diameter
        self.gamerect = pygame.Rect(left, top, diameter, diameter)
        self.update_rect()
        self.image = pygame.transform.smoothscale(
            self.image, (self.rect.width, self.rect.height))
        self.image.convert()
        self.pickup_sound = load_sound('ring_inventory.wav')

    def pickedup(self):
        self.pickup_sound.play()
        pass

    def update(self, millis):
        # hit test done in AsteroidImpactGameplayScreen
        pass

class Asteroid(VirtualGameSprite):
    def __init__(self, diameter=200, dx=4, dy=10, left=20, top=20, area=None):
        VirtualGameSprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('asteroid.png', -1)
        self.image = self.image.convert_alpha()
        self.gamediameter = diameter
        self.gamerect = pygame.Rect(left, top, diameter, diameter)
        self.update_rect()
        self.image = pygame.transform.smoothscale(
            self.image, (self.rect.width, self.rect.height))
        self.image.convert()
        if area:
            self.GAME_AREA = area
        else:
            self.GAME_AREA = virtualdisplay.GAME_AREA
        # rect uses integer positions but I need to handle fractional pixel/frame speeds.
        # store float x/y positions here:
        self.gametopfloat = float(top)
        self.gameleftfloat = float(left)
        self.dx = dx
        self.dy = dy

    def update(self, millis):
        # bounce by setting sign of x or y speed if off of corresponding side of screen
        if self.gamerect.left < self.GAME_AREA.left:
            self.dx = abs(self.dx)
        if  self.gamerect.right > self.GAME_AREA.right:
            self.dx = -abs(self.dx)
        if self.gamerect.top < self.GAME_AREA.top:
            self.dy = abs(self.dy)
        if self.gamerect.bottom > self.GAME_AREA.bottom:
            self.dy = -abs(self.dy)

        self.gameleftfloat += self.dx
        self.gametopfloat += self.dy
        self.gamerect.left = self.gameleftfloat
        self.gamerect.top = self.gametopfloat
        self.update_rect()

class BasePowerup(VirtualGameSprite):
    def __init__(self, diameter=16, left=50, top=50, maxduration=5.0):
        VirtualGameSprite.__init__(self) #call Sprite initializer
        self.gamediameter = diameter
        # likely overwritten in derived class:
        self.gamerect = pygame.Rect(left, top, diameter, diameter)
        self.update_rect()

        self.maxduration = maxduration # seconds
        self.active = False
        self.duration = 0

        self.used = False

    def update(self, millis):
        if self.active:
            self.duration += millis / 1000.

            if self.duration > self.maxduration:
                # deactivate:
                self.deactivate()

    def activate(self, *args):
        self.oldgamerect = self.gamerect.copy()
        self.active = True
        self.duration = 0
        self.used = False

    def deactivate(self, *args):
        self.active = False
        self.gamerect = self.oldgamerect
        self.update_rect()
        self.used = True
        self.kill()

class SlowPowerup(BasePowerup):
    def __init__(self, diameter=32, left=100, top=100):
        BasePowerup.__init__(self, diameter=diameter, left=left, top=top, maxduration=5.0)
        self.type = 'slow'
        self.image, self.rect = load_image('clock.png', -1)
        self.image = self.image.convert_alpha()
        self.gamerect = pygame.Rect(left, top, diameter, diameter)
        self.update_rect()
        self.image = pygame.transform.smoothscale(
            self.image, (self.rect.width, self.rect.height))
        self.sound_begin = load_sound('slow start.wav')
        self.sound_end = load_sound('slow end.wav')
        # these let me start the ending sound to end overlapping when the effect ends:
        self.sound_end_duration = self.sound_end.get_length() - 0.5
        self.sound_end_started = False


    def update(self, millis):
        BasePowerup.update(self, millis)

        if self.active:
            # start the end effect sound to end when powerup ends:
            if (self.maxduration - self.duration < self.sound_end_duration
                    and not self.sound_end_started):
                self.sound_end_started = True
                self.sound_end.play()

    def activate(self, cursor, asteroids, *args):
        BasePowerup.activate(self, *args)

        # adjust speed of asteroids
        speedfactor = 0.25
        self.asteroids = asteroids
        for asteroid in self.asteroids:
            asteroid.originaldx = asteroid.dx
            asteroid.originaldy = asteroid.dy
            asteroid.dx *= speedfactor
            asteroid.dy *= speedfactor

        # disappear offscreen
        self.gamerect.top = -10000
        self.gamerect.left = -10000
        self.update_rect()

        self.sound_begin.play()

        self.sound_end_started = False

    def deactivate(self, *args):
        BasePowerup.deactivate(self, *args)

        # restore speed of asteroids
        for asteroid in self.asteroids:
            # to keep the asteroid moving the same direction,
            # copy sign from current movement to speed of original movement
            asteroid.dx = math.copysign(asteroid.originaldx, asteroid.dx)
            asteroid.dy = math.copysign(asteroid.originaldy, asteroid.dy)

class ShieldPowerup(BasePowerup):
    def __init__(self, diameter=32, left=80, top=80):
        BasePowerup.__init__(self, diameter=diameter, left=left, top=top, maxduration=5.0)
        self.type = 'shield'
        self.image, self.rect = load_image('shield.png', -1)
        self.image = self.image.convert_alpha()
        self.gamerect = pygame.Rect(left, top, diameter, diameter)
        self.update_rect()
        self.image = pygame.transform.smoothscale(
            self.image, (self.rect.width, self.rect.height))
        self.sound_begin = load_sound('shield start.wav')
        self.sound_end = load_sound('shield end.wav')
        # these let me start the ending sound to end overlapping when the effect ends:
        self.sound_end_duration = self.sound_end.get_length() - 1.0
        self.sound_end_started = False

    def activate(self, cursor, asteroids, *args):
        BasePowerup.activate(self, *args)

        self.cursor = cursor

        self.sound_begin.play()

        self.sound_end_started = False

    def update(self, millis):
        BasePowerup.update(self, millis)
        if self.active:
            # follow on top of cursor:
            self.gamerect.center = self.cursor.gamerect.center
            self.update_rect()

            # "ignore collisions" logic happens in Game Screen

            # start the end effect sound to end when powerup ends:
            if (self.maxduration - self.duration < self.sound_end_duration
                    and not self.sound_end_started):
                self.sound_end_started = True
                self.sound_end.play()

class NonePowerup(BasePowerup):
    """This power-up has no effect except delaying the next power-up from spawning"""
    def __init__(self, duration=10.0):
        # configure as a circle completely covering the screen so I get picked up
        # as soon as available
        diameter = 10*virtualdisplay.GAME_AREA.width
        self.gamerect = pygame.Rect(0,0, diameter, diameter)
        self.gamerect.centerx = virtualdisplay.GAME_AREA.width/2
        self.gamerect.centery = virtualdisplay.GAME_AREA.height/2
        BasePowerup.__init__(
            self,
            diameter=diameter,
            left=self.gamerect.left,
            top=self.gamerect.top,
            maxduration=duration)
        self.type = 'none'
        self.image = None
        self.update_rect()
        print 'nonepowerup rect', self.gamerect
