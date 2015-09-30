import random
from sprites import *
import levels
from pygame.locals import *

# screens.py
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

class TextSprite:
	'Combines surface (bitmap) for text and drawing position to make drawing static text easier'
	def __init__(self, textsurf, **kwargs):
		self.textsurf = textsurf
		self.textrect = self.textsurf.get_rect(**kwargs)
	def draw(self, screen):
		screen.blit(self.textsurf, self.textrect)

class AsteroidImpactInstructionsScreen(GameScreen):
	def __init__(self, screen, gamescreenstack):
		GameScreen.__init__(self, screen, gamescreenstack)
		self.opaque = True
		self.screenarea = self.screen.get_rect()

		self.background = pygame.Surface(screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		self.textsprites = []
		self.sprites =  pygame.sprite.Group()

		self.font_big = load_font('freesansbold.ttf', 36)
		red = (250,10,10)
		black = (10,10,10)
		self.font = load_font('freesansbold.ttf', 16)
		self.textsprites.append(TextSprite(
			self.font_big.render("How to Play", 1, red),
			centerx=self.screenarea.width/2, top=0))

		s = Cursor()
		s.rect.topleft = (60, 60)
		self.sprites.add(s)
		self.textsprites.append(TextSprite(
			self.font.render("Move your ship around with your mouse, picking up crystals", 1, black),
			left=120, top=60))

		s = Target()
		s.rect.topleft = (60, 120)
		self.sprites.add(s)
		self.textsprites.append(TextSprite(
			self.font.render("Pick up all the crystals", 1, black),
			left=120, top=120))

		s = Asteroid(diameter=16)
		s.rect.topleft = (60, 180)
		self.sprites.add(s)
		asteroidbounds = pygame.Rect(60, 200, 480-60-60, 80)
		self.asteroids = pygame.sprite.Group([
			Asteroid(diameter=32,dx=1.5,dy=1.0,top=asteroidbounds.top,left=asteroidbounds.left,area=asteroidbounds),
			Asteroid(diameter=40,dx=2.5,dy=-1,top=asteroidbounds.top+10,left=asteroidbounds.left+200,area=asteroidbounds),
			Asteroid(diameter=20,dx=-1,dy=-3,top=asteroidbounds.top+20,left=asteroidbounds.left+300,area=asteroidbounds)])
		self.textsprites.append(TextSprite(
			self.font.render("Avoid the bouncing asteroids. Hit one and it's game over.", 1, black),
			left=120, top=180))

		s = ShieldPowerup()
		s.rect.topleft = (60, 300)
		self.sprites.add(s)
		self.textsprites.append(TextSprite(
			self.font.render("Pick up a shield to pass through asteroids for a few seconds", 1, black),
			left=120, top=300))

		s = SlowPowerup()
		s.rect.topleft = (60, 360)
		self.sprites.add(s)
		self.textsprites.append(TextSprite(
			self.font.render("Pick up a clock to slow asteroids for a few seconds", 1, black),
			left=120, top=360))

		self.textsprites.append(TextSprite(
			self.font_big.render("Click To Begin", 1, (250, 10, 10)),
			centerx=self.screenarea.width/2, bottom=self.screenarea.height))

	def draw(self):
		# draw background
		self.screen.blit(self.background, (0, 0))
		# draw all text blocks:
		for textsprite in self.textsprites:
			textsprite.draw(self.screen)
		self.sprites.draw(self.screen)
		self.asteroids.draw(self.screen)

	def update(self, millis):
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				raise QuitGame('ESC Pressed')
			elif event.type == MOUSEBUTTONDOWN:
				# position cursor at the center
				pygame.mouse.set_pos([self.screenarea.centerx, self.screenarea.centery])
				# start the game: 
				self.screenstack.pop()
				self.screenstack.append(AsteroidImpactGameplayScreen(self.screen, self.screenstack))
				self.screenstack.append(ClickToBeginOverlayScreen(self.screen, self.screenstack))
				pass
			elif event.type is MOUSEBUTTONUP:
				pass
		
		# update asteroid positions
		for asteroid in self.asteroids:
			asteroid.update(millis)


class ClickToBeginOverlayScreen(GameScreen):
	def __init__(self, screen, gamescreenstack):
		GameScreen.__init__(self, screen, gamescreenstack)
		self.opaque = False
		self.screenarea = self.screen.get_rect()
		self.font = load_font('freesansbold.ttf', 36)
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

class LevelCompletedOverlayScreen(GameScreen):
	def __init__(self, screen, gamescreenstack):
		GameScreen.__init__(self, screen, gamescreenstack)
		self.opaque = False
		self.screenarea = self.screen.get_rect()
		self.font = load_font('freesansbold.ttf', 36)
		self.text = self.font.render("Level Completed", 1, (250, 10, 10))
		self.textpos = self.text.get_rect(centerx=self.screenarea.width/2,centery=self.screenarea.height/2)

	def draw(self):
		self.screen.blit(self.text, self.textpos)
		pass

	def update(self, millis):
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				raise QuitGame('ESC Pressed')
			elif event.type == MOUSEBUTTONDOWN:
				if len(self.screenstack) > 1 and isinstance(self.screenstack[-2], AsteroidImpactGameplayScreen):
					# advance to next level
					self.screenstack[-2].advance_level()
				# remove 'level completed' screen
				self.screenstack.pop()
				# add 'click to begin' screen
				self.screenstack.append(ClickToBeginOverlayScreen(self.screen, self.screenstack))
			elif event.type is MOUSEBUTTONUP:
				pass

class GameOverOverlayScreen(GameScreen):
	def __init__(self, screen, gamescreenstack):
		GameScreen.__init__(self, screen, gamescreenstack)
		self.opaque = False
		self.screenarea = self.screen.get_rect()
		self.font = load_font('freesansbold.ttf', 36)
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

def circularspritesoverlap(a, b):
	x1 = a.rect.centerx
	y1 = a.rect.centery
	d1 = a.diameter
	x2 = b.rect.centerx
	y2 = b.rect.centery
	d2 = b.diameter
	# x1, y1, d1, x2, y2, d2
	return ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)) < (.25*(d1 + d2)*(d1 + d2))

def make_powerup(powerup_dict):
	# copy so that removing 'type' doesn't change original
	powerup_dict = dict(powerup_dict) 
	type = powerup_dict.pop('type')
	if type == 'shield':
		return ShieldPowerup(**powerup_dict)
	if type == 'slow':
		return SlowPowerup(**powerup_dict)
	if type == 'none':
		return NonePowerup(**powerup_dict)
	print 'ERROR: Unknown type of powerup in level: ', type


class AsteroidImpactGameplayScreen(GameScreen):
	def __init__(self, screen, screenstack):
		GameScreen.__init__(self, screen, screenstack)
		self.screenarea = self.screen.get_rect()
		self.background = pygame.Surface(screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		self.statusfont = load_font('freesansbold.ttf', 36)
		self.statustext = self.statusfont.render('Placeholder Art', 1, (10, 10, 10))
		self.statustextrect = self.statustext.get_rect(centerx=self.background.get_width()/2)
			
		self.sound_death = load_sound('DeathFlash.wav')

		#Display The Background
		self.screen.blit(self.background, (0, 0))
		self.level_list = levels.get_levels(self.screenarea)
		if len(self.level_list) == 0:
			print 'ERROR: Level list is empty'
			raise QuitGame
		self.level_index = 0
		self.setup_level()
	
		
	def setup_level(self):
		leveldetails = self.level_list[self.level_index]
		self.levelmillis = 0
		
		self.cursor = Cursor()
		self.target_positions = leveldetails['target_positions']
		self.target_index = 0
		self.target = Target(diameter=16, left=self.target_positions[0][0], top=self.target_positions[0][1])
		self.asteroids = [Asteroid(**d) for d in leveldetails['asteroids']]
		self.powerup_list = [make_powerup(d) for d in leveldetails['powerup_list']]
		self.powerup = self.powerup_list[0]
		self.next_powerup_list_index = 1 % len(self.powerup_list)
		self.mostsprites = pygame.sprite.OrderedUpdates(self.asteroids + [self.cursor, self.target])
		self.powerupsprites = pygame.sprite.Group()
		if self.powerup.image:
			self.powerupsprites.add(self.powerup)
		self.update_status_text()

	def advance_level(self):
		self.level_index = (self.level_index + 1) % len(self.level_list)
		self.setup_level()
	
	def update_status_text(self):
		# todo: update the text
		statusblurb = '%d/%d collected %2.2f seconds'%(self.target_index, len(self.target_positions), self.levelmillis / 1000.)
		self.statustext = self.statusfont.render(statusblurb, 1, (10, 10, 10))
		self.statustextrect = self.statustext.get_rect(centerx=self.background.get_width()/2)


	def update(self, millis):
		self.levelmillis += millis
		
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
			self.powerupsprites.empty()
			if self.powerup.image:
				self.powerupsprites.add(self.powerup)
			self.next_powerup_list_index = (1 + self.next_powerup_list_index) % len(self.powerup_list)
		self.powerup.update(millis)
		
		# additional game logic:
		if circularspritesoverlap(self.cursor, self.target):
			# hit. 
			# todo: increment counter of targets hit
			self.target.pickedup()
			self.target_index += 1
			if self.target_index >= len(self.target_positions):
				# TODO: record level completion duration
				print 'completed level'
				self.screenstack.append(LevelCompletedOverlayScreen(self.screen, self.screenstack))
			else:
				# position for next crystal target:
				self.target.rect.left = self.target_positions[self.target_index][0]
				self.target.rect.top = self.target_positions[self.target_index][1]
		for asteroid in self.asteroids:
			if circularspritesoverlap(self.cursor, asteroid):
				# todo: find a cleaner way to have the shield powerup do this work:
				if not (self.powerup != None and self.powerup.__class__ == ShieldPowerup and self.powerup.active):
					self.sound_death.play()
					print 'dead', self.cursor.rect.left, self.cursor.rect.top
					self.screenstack.append(GameOverOverlayScreen(self.screen, self.screenstack))
					break
		# powerups?
		if self.powerup != None \
			and circularspritesoverlap(self.cursor, self.powerup) \
			and not self.powerup.active \
			and not self.powerup.used:
			print 'hit powerup', self.cursor.rect.left, self.cursor.rect.top, self.powerup
			# TODO: decide where and when to spawn next powerup
			# how should powerup behavior be implemented?
			self.powerup.activate(self.cursor, self.asteroids)
		
		self.update_status_text()

	def draw(self):
		self.screen.blit(self.background, (0, 0))
		self.screen.blit(self.statustext, self.statustextrect)
		self.mostsprites.draw(self.screen)
		self.powerupsprites.draw(self.screen)

