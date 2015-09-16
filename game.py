'''
'Asteroid Impact'
Copyright (c) 2015 Nick Winters
'''

# to make python3 porting easier:
# see http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/
from __future__ import absolute_import, division
'''
>>> 6 / 7
1
>>> from __future__ import division
>>> 6 / 7
1.2857142857142858
'''


#Import Modules
import os, pygame
from pygame.locals import *
import random

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


#functions to create our resources
def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', fullname
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

def load_sound(name):
	class NoneSound:
		def play(self): pass
	if not pygame.mixer or not pygame.mixer.get_init():
		return NoneSound()
	fullname = os.path.join('data', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'Cannot load sound:', fullname
		raise SystemExit, message
	return sound


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

	def update(self, millis):
		# hit test done in AsteroidImpactGameplayScreen
		pass

class Asteroid(pygame.sprite.Sprite):
	def __init__(self, diameter=100, dx=2, dy=5, left=10, top=10):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.image, self.rect = load_image('asteroid.png', -1)
		self.image = self.image.convert_alpha()
		self.diameter = diameter
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.top = top
		self.rect.left = left
		self.dx = dx
		self.dy = dy

	def update(self, millis):
		newpos = self.rect.move((self.dx, self.dy))
		if self.rect.left < self.area.left or self.rect.right > self.area.right:
			self.dx = -self.dx
		if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
			self.dy = -self.dy
		newpos = self.rect.move((self.dx, self.dy))
		self.rect = newpos

class BasePowerup(pygame.sprite.Sprite):
	def __init__(self):
		pass
	def update(self, millis):
		pass

class SlowPowerup(pygame.sprite.Sprite):
	def __init__(self, diameter=16, left=50, top=50):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('icecube.png', -1)
		self.image = self.image.convert_alpha()
		self.diameter = diameter
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		self.rect.left = left
		self.rect.top = top

		self.duration = 5.0 # seconds
		self.active = False
		self.timeremaining = 0

	def update(self, millis):
		# hit test done in AsteroidImpactGameplayScreen
		pass
		
class ShieldPowerup(pygame.sprite.Sprite):
	def __init__(self, diameter=16, left=40, top=40):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('shield.png', -1)
		self.image = self.image.convert_alpha()
		self.diameter = diameter
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		self.rect.left = left
		self.rect.top = top

		self.maxduration = 5.0 # seconds
		self.active = False
		self.duration = 0
		
		self.used = False

	def update(self, millis):
		if (self.active):
			# follow on top of cursor:
			pos = pygame.mouse.get_pos()
			self.rect.center = pos

			self.duration += millis / 1000.
			
			if self.duration > self.maxduration:
				# deactivate:
				self.active = False
				self.rect = self.oldrect
				self.used = True
				self.kill()

	def activate(self, *args):
		self.oldrect = self.rect.copy()
		self.active = True
		self.duration = 0
		self.used = False

class QuitGame(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class GameScreen():
	def __init__(self, screen, screenstack):
		self.screen = screen
		self.screenstack = screenstack
		self.opaque = True
		
	def update(self, millis):
		pass
	
	def draw(self):
		# TODO: fill entire screen with a unique color to indicate that draw() is being called here
		pass

def circularspritesoverlap(a, b):
	x1 = a.rect.centerx
	y1 = a.rect.centery
	d1 = a.diameter
	x2 = b.rect.centerx
	y2 = b.rect.centery
	d2 = b.diameter
	# x1, y1, d1, x2, y2, d2
	return ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)) < (.25*(d1 + d2)*(d1 + d2))

class ClickToBeginOverlayScreen(GameScreen):
	def __init__(self, screen, gamescreenstack):
		GameScreen.__init__(self, screen, gamescreenstack)
		self.opaque = False
		self.screenarea = self.screen.get_rect()
		if pygame.font:
			self.font = pygame.font.Font(None, 36)
			self.text = self.font.render("Click To Begin", 1, (250, 10, 10))
			self.textpos = self.text.get_rect(centerx=self.screenarea.width/2,centery=self.screenarea.height/2)

	def draw(self):
		self.screen.blit(self.text, self.textpos)
		pass

	def update(self, millis):
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				raise QuitGame('ESC Pressed')
			elif event.type == MOUSEBUTTONDOWN:
				self.screenstack.pop()
				pass
			elif event.type is MOUSEBUTTONUP:
				pass
				
		if len(self.screenstack) > 1 and isinstance(self.screenstack[-2], AsteroidImpactGameplayScreen):
			# update cursor:
			self.screenstack[-2].cursor.update(millis)

class GameOverOverlayScreen(GameScreen):
	def __init__(self, screen, gamescreenstack):
		GameScreen.__init__(self, screen, gamescreenstack)
		self.opaque = False
		self.screenarea = self.screen.get_rect()
		if pygame.font:
			self.font = pygame.font.Font(None, 36)
			self.text = self.font.render("Game Over", 1, (250, 10, 10))
			self.textpos = self.text.get_rect(centerx=self.screenarea.width/2,centery=self.screenarea.height/2)

	def draw(self):
		self.screen.blit(self.text, self.textpos)
		pass

	def update(self, millis):
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				raise QuitGame('ESC Pressed')
			elif event.type == MOUSEBUTTONDOWN:
				self.screenstack.pop()
				if isinstance(self.screenstack[-1], AsteroidImpactGameplayScreen):
					self.screenstack.pop()
				# start game over
				self.screenstack.append(AsteroidImpactGameplayScreen(self.screen, self.screenstack))
				self.screenstack.append(ClickToBeginOverlayScreen(self.screen, self.screenstack))
			elif event.type is MOUSEBUTTONUP:
				pass

class AsteroidImpactGameplayScreen(GameScreen):
	def __init__(self, screen, screenstack):
		GameScreen.__init__(self, screen, screenstack)
		self.screenarea = self.screen.get_rect()
		self.background = pygame.Surface(screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		if pygame.font:
			self.font = pygame.font.Font(None, 36)
			text = self.font.render("Placeholder Art", 1, (10, 10, 10))
			textpos = text.get_rect(centerx=self.background.get_width()/2)
			self.background.blit(text, textpos)

		#Display The Background
		self.screen.blit(self.background, (0, 0))
		
		self.rnd = random.Random(3487437)
		self.cursor = Cursor()
		self.target = Target(diameter=16, left=self.rnd.randint(0, self.screenarea.width - 16), top=self.rnd.randint(0, self.screenarea.height - 16))
		self.asteroids = [Asteroid(diameter=100, dx=2, dy=5, top=100, left=10),
			Asteroid(diameter=80, dx=4, dy=3, top=200, left=50),
			Asteroid(diameter=60, dx=-5, dy=-3, top=120, left=400)]
		self.powerup_list = [
			#SlowPowerup(diameter=16, left=self.rnd.randint(0, self.screenarea.width - 16), top=self.rnd.randint(0, self.screenarea.height - 16)),
			ShieldPowerup(diameter=16, left=self.rnd.randint(0, self.screenarea.width - 16), top=self.rnd.randint(0, self.screenarea.height - 16)),
			ShieldPowerup(diameter=16, left=self.rnd.randint(0, self.screenarea.width - 16), top=self.rnd.randint(0, self.screenarea.height - 16)),
			ShieldPowerup(diameter=16, left=self.rnd.randint(0, self.screenarea.width - 16), top=self.rnd.randint(0, self.screenarea.height - 16)),	
			]
		self.powerup = self.powerup_list[0]
		self.next_powerup_list_index = 1 % len(self.powerup_list)
		self.mostsprites = pygame.sprite.OrderedUpdates(self.asteroids + [self.cursor, self.target])
		self.powerupsprites = pygame.sprite.Group(self.powerup)

	def update(self, millis):
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				raise QuitGame('ESC Pressed')
			elif event.type == MOUSEBUTTONDOWN:
				pass
			elif event.type is MOUSEBUTTONUP:
				pass

		self.mostsprites.update(millis)
		# update powerups
		# if current power-up has been used completely:
		if self.powerup.used:
			# switch to and get ready next one:
			self.powerup = self.powerup_list[self.next_powerup_list_index]
			self.powerup.used = False
			print self.powerup.rect
			self.powerupsprites.empty()
			self.powerupsprites.add(self.powerup)
			self.next_powerup_list_index = (1 + self.next_powerup_list_index) % len(self.powerup_list)
		self.powerupsprites.update(millis)
		
		# additional game logic:
		if circularspritesoverlap(self.cursor, self.target):
			# hit. 
			# todo: increment counter of targets hit
			print 'hit!'
			# reposition target
			self.target.rect.left = self.rnd.randint(0, self.screenarea.width - self.target.diameter)
			self.target.rect.top = self.rnd.randint(0, self.screenarea.height - self.target.diameter)
		for asteroid in self.asteroids:
			if circularspritesoverlap(self.cursor, asteroid):
				# todo: find a cleaner way to have the shield powerup do this work:
				if not (self.powerup != None and self.powerup.__class__ == ShieldPowerup and self.powerup.active):
					print 'dead', self.cursor.rect.left, self.cursor.rect.top
					self.screenstack.append(GameOverOverlayScreen(self.screen, self.screenstack))
		# powerups?
		if self.powerup != None \
			and circularspritesoverlap(self.cursor, self.powerup) \
			and not self.powerup.active \
			and not self.powerup.used:
			print 'hit powerup', self.cursor.rect.left, self.cursor.rect.top, self.powerup
			# TODO: decide where and when to spawn next powerup
			# how should powerup behavior be implemented?
			self.powerup.activate(self.cursor, self.asteroids)

	def draw(self):
		self.screen.blit(self.background, (0, 0))
		self.mostsprites.draw(self.screen)
		self.powerupsprites.draw(self.screen)



def main():
	pygame.init()
	screen = pygame.display.set_mode((640, 480))
	pygame.display.set_caption('Asteroid Impact')
	pygame.mouse.set_visible(0)
	
	gamescreenstack = []
	gamescreenstack.append(AsteroidImpactGameplayScreen(screen, gamescreenstack))
	gamescreenstack.append(ClickToBeginOverlayScreen(screen, gamescreenstack))
	
	pygame.display.flip()

	#Prepare Game Objects
	clock = pygame.time.Clock()

	#Main Loop
	while 1:
		millis = clock.tick(60)

		#Handle Input Events
		for event in pygame.event.get(QUIT):
			if event.type == QUIT:
				return		
		
		try:
			gamescreenstack[-1].update(millis)
		except QuitGame as e:
			print e
			return

		# draw topmost opaque screen and everything above it
		topopaquescreenindex = -1
		for i in range(-1, -1-len(gamescreenstack), -1):
			topopaquescreenindex = i
			if gamescreenstack[i].opaque:
				break

		for screenindex in range(topopaquescreenindex, 0, 1):
			gamescreenstack[screenindex].draw()
		
		pygame.display.flip()

#Game Over

if __name__ == '__main__': main()