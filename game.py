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
		self.diameter = 50
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
		self.diameter = 50
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter

	def update(self):
		# hit test done in Cursor
		pass

class Asteroid(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.image, self.rect = load_image('asteroid.png', -1)
		self.diameter = 100
		self.image = pygame.transform.smoothscale(self.image, (self.diameter, self.diameter))
		self.image.convert()
		self.rect.width = self.diameter
		self.rect.height = self.diameter
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = 10, 10
		self.dx = 2
		self.dy = 5

	def update(self):
		newpos = self.rect.move((self.dx, self.dy))
		if self.rect.left < self.area.left or self.rect.right > self.area.right:
			self.dx = -self.dx
		if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
			self.dy = -self.dy
		newpos = self.rect.move((self.dx, self.dy))
		self.rect = newpos

def circularspritesoverlap(a, b):
	x1 = a.rect.centerx
	y1 = a.rect.centery
	d1 = a.diameter
	x2 = b.rect.centerx
	y2 = b.rect.centery
	d2 = b.diameter
	# x1, y1, d1, x2, y2, d2
	return ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)) < ((d1 * d1 + d2 * d2) / 2.)

def main():
	pygame.init()
	screen = pygame.display.set_mode((640, 480))
	pygame.display.set_caption('Asteroid Impact')
	pygame.mouse.set_visible(0)

	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))

	if pygame.font:
		font = pygame.font.Font(None, 36)
		text = font.render("Test", 1, (10, 10, 10))
		textpos = text.get_rect(centerx=background.get_width()/2)
		background.blit(text, textpos)

	#Display The Background
	screen.blit(background, (0, 0))
	pygame.display.flip()

	#Prepare Game Objects
	clock = pygame.time.Clock()
	#whiff_sound = load_sound('whiff.wav')
	#punch_sound = load_sound('punch.wav')
	cursor = Cursor()
	target = Target()
	asteroids = [Asteroid()]
	allsprites = pygame.sprite.RenderPlain(asteroids + [target, cursor])
	rnd = random.Random(3487437)
	screenarea = screen.get_rect()

	#Main Loop
	while 1:
		clock.tick(60)

		#Handle Input Events
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			elif event.type == MOUSEBUTTONDOWN:
				pass
				#if fist.punch(chimp):
				#	punch_sound.play() #punch
				#	chimp.punched()
				#else:
				#	whiff_sound.play() #miss
			elif event.type is MOUSEBUTTONUP:
				pass
				#fist.unpunch()

		allsprites.update()
		
		# additional game logic:
		if circularspritesoverlap(cursor, target):
			# hit. 
			# todo: increment counter of targets hit
			print 'hit!'
			# reposition target
			target.rect.left = rnd.randint(0, screenarea.width - target.diameter)
			target.rect.top = rnd.randint(0, screenarea.height - target.diameter)
		for asteroid in asteroids:
			if circularspritesoverlap(cursor, asteroid):
				print 'dead', cursor.rect.left, cursor.rect.top
				# todo: restart level or somesuch			

		#Draw Everything
		screen.blit(background, (0, 0))
		allsprites.draw(screen)
		pygame.display.flip()

#Game Over

if __name__ == '__main__': main()