from __future__ import absolute_import, division
import os, pygame

# Changing these only takes effect on newly loaded sounds
# so set volume before any sounds are loaded
music_volume = 1.0
effects_volume = 1.0

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
		image.set_colorkey(colorkey, pygame.locals.RLEACCEL)
	return image, image.get_rect()

def load_sound(name):
	class NoneSound:
		def __init(self):
			self.volume = 1.0
		def play(self): pass
		def stop(self): pass
		def get_length(self): return 1.0 #seconds
		def set_volume(self, volume): self.volume = volume
		def get_volume(self): return self.volume
	if not pygame.mixer or not pygame.mixer.get_init():
		return NoneSound()
	fullname = os.path.join('data', name)
	try:
		sound = pygame.mixer.Sound(fullname)
		sound.set_volume(effects_volume)
	except pygame.error, message:
		print 'Cannot load sound:', fullname
		raise SystemExit, message
	return sound
	
def load_music(name):
	if not pygame.mixer or not pygame.mixer.get_init():
		return
	fullname = os.path.join('data', name)
	try:
		pygame.mixer.music.load(fullname)
	except pygame.error, message:
		print 'Cannot load music:', fullname
		raise SystemExit, message
