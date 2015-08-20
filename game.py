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
		self.image.convert_alpha()
		self.diameter = 16
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		self.punching = 0

	def update(self):
		"move the fist based on the mouse position"
		pos = pygame.mouse.get_pos()
		self.rect.center = pos

class Target(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('target.png', -1)
		self.diameter = 16
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter

	def update(self):
		# hit test done in Cursor
		pass

class Asteroid(pygame.sprite.Sprite):
	def __init__(self, diameter=100, dx=2, dy=5, top=10, left=10):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.image, self.rect = load_image('asteroid.png', -1)
		self.diameter = diameter
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = top, left
		self.dx = dx
		self.dy = dy

	def update(self):
		newpos = self.rect.move((self.dx, self.dy))
		if self.rect.left < self.area.left or self.rect.right > self.area.right:
			self.dx = -self.dx
		if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
			self.dy = -self.dy
		newpos = self.rect.move((self.dx, self.dy))
		self.rect = newpos

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
		
	def update(self):
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
	return ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)) < ((d1 * d1 + d2 * d2) / 2.)

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

	def update(self):
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
			self.screenstack[-2].cursor.update()

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

	def update(self):
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
			text = self.font.render("Test", 1, (10, 10, 10))
			textpos = text.get_rect(centerx=self.background.get_width()/2)
			self.background.blit(text, textpos)

		#Display The Background
		self.screen.blit(self.background, (0, 0))
		
		self.cursor = Cursor()
		self.target = Target()
		self.asteroids = [Asteroid(diameter=100, dx=2, dy=5, top=100, left=10),
			Asteroid(diameter=80, dx=4, dy=3, top=200, left=50),
			Asteroid(diameter=60, dx=-5, dy=-3, top=120, left=400)]
		self.allsprites = pygame.sprite.RenderPlain(self.asteroids + [self.target, self.cursor])
		self.rnd = random.Random(3487437)

	def update(self):
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				raise QuitGame('ESC Pressed')
			elif event.type == MOUSEBUTTONDOWN:
				pass
			elif event.type is MOUSEBUTTONUP:
				pass

		self.allsprites.update()
		
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
				print 'dead', self.cursor.rect.left, self.cursor.rect.top
				self.screenstack.append(GameOverOverlayScreen(self.screen, self.screenstack))

	def draw(self):
		self.screen.blit(self.background, (0, 0))
		self.allsprites.draw(self.screen)
	



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
		clock.tick(60)

		#Handle Input Events
		for event in pygame.event.get(QUIT):
			if event.type == QUIT:
				return		
		
		try:
			gamescreenstack[-1].update()
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