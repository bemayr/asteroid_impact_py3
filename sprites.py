import pygame
from resources import *
import math

#classes for our game objects
class Cursor(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('cursor.png', -1)
		self.image = self.image.convert_alpha()
		self.diameter = 16
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		self.punching = 0

	def update(self, millis):
		"move the fist based on the mouse position"
		pos = pygame.mouse.get_pos()
		self.rect.center = pos 

class Target(pygame.sprite.Sprite):
	def __init__(self, diameter=16, left=10, top=10):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('target.png', -1)
		self.image = self.image.convert_alpha()
		self.diameter = diameter
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		self.rect.top = top
		self.rect.left = left
		self.pickup_sound = load_sound('ring_inventory.wav')
	
	def pickedup(self):
		self.pickup_sound.play()
		pass
		
	def update(self, millis):
		# hit test done in AsteroidImpactGameplayScreen
		pass

class Asteroid(pygame.sprite.Sprite):
	def __init__(self, diameter=100, dx=2, dy=5, left=10, top=10, area=None):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.image, self.rect = load_image('asteroid.png', -1)
		self.image = self.image.convert_alpha()
		self.diameter = diameter
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		screen = pygame.display.get_surface()
		self.area = area
		if not self.area:
			self.area = screen.get_rect()
		self.rect.top = top
		self.rect.left = left
		# rect uses integer positions but I need to handle fractional pixel/frame speeds.
		# store float x/y positions here:
		self.topfloat = float(top)
		self.leftfloat = float(left)
		self.dx = dx
		self.dy = dy

	def update(self, millis):
		# bounce by setting sign of x or y speed if off of corresponding side of screen
		if self.rect.left < self.area.left:
			self.dx = abs(self.dx)
		if  self.rect.right > self.area.right:
			self.dx = -abs(self.dx)
		if self.rect.top < self.area.top:
			self.dy = abs(self.dy)
		if self.rect.bottom > self.area.bottom:
			self.dy = -abs(self.dy)
			
		self.leftfloat += self.dx
		self.topfloat += self.dy
 		self.rect.left = self.leftfloat
 		self.rect.top = self.topfloat

class BasePowerup(pygame.sprite.Sprite):
	def __init__(self, diameter=16, left=50, top=50, maxduration=5.0):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.diameter = diameter
		self.rect = pygame.Rect(left, top, diameter, diameter) # likely overwritten in derived class

		self.maxduration = maxduration # seconds
		self.active = False
		self.duration = 0
		
		self.used = False

	def update(self, millis):
		if (self.active):
			self.duration += millis / 1000.
			
			if self.duration > self.maxduration:
				# deactivate:
				self.deactivate()

	def activate(self, *args):
		self.oldrect = self.rect.copy()
		self.active = True
		self.duration = 0
		self.used = False
		
	def deactivate(self, *args):
		self.active = False
		self.rect = self.oldrect
		self.used = True
		self.kill()

class SlowPowerup(BasePowerup):
	def __init__(self, diameter=16, left=50, top=50):
		BasePowerup.__init__(self, diameter=diameter, left=left, top=top, maxduration=5.0)
		self.image, self.rect = load_image('icecube.png', -1)
		self.image = self.image.convert_alpha()
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		self.rect.left = left
		self.rect.top = top
		self.sound_begin = load_sound('slow start.wav')
		self.sound_end = load_sound('slow end.wav')
		# these let me start the ending sound to end overlapping when the effect ends:
		self.sound_end_duration = self.sound_end.get_length() - 0.5
		self.sound_end_started = False


	def update(self, millis):
		BasePowerup.update(self, millis)
		
		if self.active:
			# start the end effect sound to end when powerup ends:
			if self.maxduration - self.duration < self.sound_end_duration \
				and not self.sound_end_started:
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
		self.rect.top = -100
		self.rect.left = -100

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
	def __init__(self, diameter=16, left=40, top=40):
		BasePowerup.__init__(self, diameter=diameter, left=left, top=top, maxduration=5.0)
		self.image, self.rect = load_image('shield.png', -1)
		self.image = self.image.convert_alpha()
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		self.rect.left = left
		self.rect.top = top
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
		if (self.active):
			# follow on top of cursor:
			#pos = pygame.mouse.get_pos()
			#self.rect.center = pos
			self.rect = self.cursor.rect

			# "ignore collisions" logic happens in Game Screen

			# start the end effect sound to end when powerup ends:
			if self.maxduration - self.duration < self.sound_end_duration \
				and not self.sound_end_started:
				self.sound_end_started = True
				self.sound_end.play()

class NonePowerup(BasePowerup):
	'''This power-up has no effect except delaying the next power-up from spawning'''
	def __init__(self, duration=10.0):
		# configure as a circle completely covering the screen so I get picked up as soon as available
		BasePowerup.__init__(self, diameter=2000, left=0, top=0, maxduration=duration)
		self.image = None
