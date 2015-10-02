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
import argparse
from os import path
import json
import pygame
from pygame.locals import *


if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

from screens import *
import resources

# command-line arguments:
parser = argparse.ArgumentParser(description='Run Asteroid Impact game.')
parser.add_argument('--music-volume', type=float, default=1.0,
	help='music volume, 1.0 for full')
parser.add_argument('--effects-volume', type=float, default=1.0,
	help='sound effects volume, 1.0 for full')
parser.add_argument('--display-width', type=int, default=640,
	help='Width of window or full screen mode.')
parser.add_argument('--display-height', type=int, default=480,
	help='Height of window or full screen mode.')
parser.add_argument('--display-mode', choices=['windowed','fullscreen'], default='windowed',
	help='Whether to run windowed or fullscreen')
parser.add_argument('--levels-json', type=str, default=None,
	help='levellist.json file listing all levels to complete.')

def load_levels(dir, levellistfile):
	# load level list
	with open(path.join(dir, levellistfile)) as f:
		levellist = json.load(f)
	
	# load all levels in list
	levels = []
	for levelfile in levellist['levels']:
		with open(path.join(dir, levelfile)) as f:
			levels.append(json.load(f))
	
	# todo: validate levels?

	return levels


def main():
	args = parser.parse_args()
	resources.music_volume = args.music_volume
	resources.effects_volume = args.effects_volume
	
	# load levels
	if args.levels_json != None:
		if not path.exists(args.levels_json):
			print 'Error: Could not find file at "%s"'%args.levels_json
			return
		levelsabspath = os.path.abspath(args.levels_json)
		levelsdir,levelsfilename = os.path.split(levelsabspath)
		levellist = load_levels(levelsdir, levelsfilename)
	else:
		levellist = load_levels('levels', 'standardlevels.json')
	
	if pygame.mixer:
		pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
	pygame.init()
	displayflags = 0
	if args.display_mode == 'fullscreen':
		displayflags |= pygame.FULLSCREEN
	screensize = (args.display_width, args.display_height)
	virtualdisplay.set_screensize(screensize)
	screen = pygame.display.set_mode(screensize, displayflags)
	pygame.display.set_caption('Asteroid Impact')
	pygame.mouse.set_visible(0)
	# capture mouse
	pygame.event.set_grab(True)
	
	gamescreenstack = []
	gamescreenstack.append(AsteroidImpactInstructionsScreen(screen, gamescreenstack))
	
	pygame.display.flip()

	#Prepare Game Objects
	clock = pygame.time.Clock()

	if pygame.mixer:
		load_music('through space.ogg')
		pygame.mixer.music.set_volume(resources.music_volume)
		pygame.mixer.music.play()
	
	
	#Main Loop
	while 1:
		millis = clock.tick(60)

		#Handle Input Events
		for event in pygame.event.get(QUIT):
			if event.type == QUIT:
				return
		
		# update the topmost screen:
		try:
			gamescreenstack[-1].update(millis)
		except QuitGame as e:
			print e
			return

		if len(gamescreenstack) == 0:
			# Switch to gameplay
			gamescreenstack.append(AsteroidImpactGameplayScreen(screen, gamescreenstack, levellist))

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