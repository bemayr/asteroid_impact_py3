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
import os
from os import path
import json
import pygame
from pygame.locals import *


if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

from screens import *
import resources
from logger import AsteroidLogger

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
parser.add_argument('--window-x', type=int, default=None,
	help='X position of window.')
parser.add_argument('--window-y', type=int, default=None,
	help='Y position of window.')
parser.add_argument('--display-mode', choices=['windowed','fullscreen'], default='windowed',
	help='Whether to run windowed or fullscreen')
parser.add_argument('--levels-json', type=str, default=None,
	help='levellist.json file listing all levels to complete.')


class GameModeManager:
	'''follow the instructions to switch between game screens, and levels
	Rather than specifying a single level list, specify a file that has a list of entries where each entry specifies the following:
	Action: Either Instructions, Game, or Black Screen
	Levels: For the game, the list of level files to play. The player will progress (or not) through them in order, and after completing the last level will start again at the beginning. Dying will restart the current level.
	Duration: After this many seconds move to the next step, regardless of what the player is doing now.
	'''
	def __init__(self, args):
		# TODO: look for this on the command-line:
		self.gamesteps = [
			dict(action='instructions',
				duration=5.0),
			dict(action='game',
				levels='levels/standardlevels.json',
				duration=None)]
		
			# load levels
		if args.levels_json != None:
			if not path.exists(args.levels_json):
				raise 'Error: Could not find file at "%s"'%args.levels_json
			levelsabspath = os.path.abspath(args.levels_json)
			levelsdir,levelsfilename = os.path.split(levelsabspath)
			self.levellist = self.load_levels(levelsdir, levelsfilename)
		else:
			self.levellist = self.load_levels('levels', 'standardlevels.json')

		# TODO: add log file to command-line arguments
		# TODO: add 'participant ID' to command-line arguments. Use current date/time if not supplied?
		
		resources.music_volume = args.music_volume
		resources.effects_volume = args.effects_volume

		if pygame.mixer:
			pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)

		displayflags = pygame.DOUBLEBUF
		if args.display_mode == 'fullscreen':
			displayflags |= pygame.FULLSCREEN
		else:
			# windowed
			displayflags |= pygame.NOFRAME
			if args.window_x != None and args.window_y != None:
				os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (args.window_x,args.window_y)
		screensize = (args.display_width, args.display_height)
		virtualdisplay.set_screensize(screensize)

		pygame.init()
		self.screen = pygame.display.set_mode(screensize, displayflags)
		pygame.display.set_caption('Asteroid Impact')
		pygame.mouse.set_visible(0)
		# capture mouse
		pygame.event.set_grab(True)

		pygame.display.flip()

		# Init sequence of steps:
		self.stepindex = 0
		self.init_step()
	
	def init_step(self):
		self.step_millis = 0
		step = self.gamesteps[self.stepindex]
		self.step_max_millis = None
		if step.has_key('duration') and step['duration'] != None:
			self.step_max_millis = int(1000 * step['duration'])
		self.gamescreenstack = []
		if step['action'] == 'instructions':
			self.gamescreenstack.append(AsteroidImpactInstructionsScreen(self.screen, self.gamescreenstack))
		elif step['action'] == 'game':		
			self.gamescreenstack.append(AsteroidImpactGameplayScreen(self.screen, self.gamescreenstack, self.levellist))
		else:
			raise ValueError('Unknown step action "%s"'%step.action)


	def load_levels(self, dir, levellistfile):
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
			
	def gameloop(self):
		clock = pygame.time.Clock()

		if pygame.mixer:
			load_music('through space.ogg')
			pygame.mixer.music.set_volume(resources.music_volume)
			pygame.mixer.music.play()
	
		asteroidlogger = AsteroidLogger()
		logrowdetails = {}

		self.total_millis = 0
		
		# cheesy 'framerate' display
		# mostly used to indicate if I'm getting 60fps or 30fps
		fps_display_enable = True
		import sprites
		fps_sprite = Target(diameter=8)
		fps_sprite.rect.top = 0
		fps_sprite_group = pygame.sprite.Group([fps_sprite])
	
		#Main Loop
		while 1:
			# more consistent, more cpu
			real_millis = clock.tick_busy_loop(60)
			# less repeatable, less cpu:
			#real_millis = clock.tick(60)
			
			if real_millis >= 25:
				# if we're not getting 60fps, then run update() extra times
				# find new frame durations that add-up to real_millis:
				frames = int(round(real_millis * .001 * 60))
				millis_list = [16] * frames
				millis_list[-1] = real_millis - 16 * (frames-1)
			else:
				millis_list = (real_millis,)

			for millis in millis_list:
				self.total_millis += millis
				self.step_millis += millis

				logrowdetails.clear()
				logrowdetails['total_millis'] = self.total_millis
				logrowdetails['step_number'] = self.stepindex + 1
				logrowdetails['step_millis'] = self.step_millis
				logrowdetails['top_screen'] = self.gamescreenstack[-1].name
				# TODO:
				#player [specified on command line]
				#experimental condition filename
				#experimental condition step index

				#Handle Input Events
				for event in pygame.event.get(QUIT):
					if event.type == QUIT:
						return
		
				# update the topmost screen:
				try:
					self.gamescreenstack[-1].update(millis, logrowdetails)
				except QuitGame as e:
					print e
					return

				# Check if max duration on this step has expired
				step = self.gamesteps[self.stepindex]
				if self.step_max_millis != None and self.step_max_millis < self.step_millis:
					# end this step:
					self.gamescreenstack = []

				if len(self.gamescreenstack) == 0:
					self.stepindex += 1
					if self.stepindex >= len(self.gamesteps):
						# all steps completed
						return
					self.init_step()
					# Switch to gameplay

			# draw topmost opaque screen and everything above it
			topopaquescreenindex = -1
			for i in range(-1, -1-len(self.gamescreenstack), -1):
				topopaquescreenindex = i
				if self.gamescreenstack[i].opaque:
					break

			for screenindex in range(topopaquescreenindex, 0, 1):
				self.gamescreenstack[screenindex].draw()
				
			# cheesy 'no text' FPS display
			fps_sprite.rect.left = real_millis
			fps_sprite.rect.top = 16 * (int(round(real_millis * .001 * 60))-1)
			if fps_display_enable:
				fps_sprite_group.draw(self.screen)
		
			pygame.display.flip()
		
			asteroidlogger.log(logrowdetails)
			

def main():
	args = parser.parse_args()

	game_step_manager = GameModeManager(args)
	game_step_manager.gameloop()

if __name__ == '__main__': 
	main()
