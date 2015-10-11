"""
Game screens for AsteroidImpact
"""

from sprites import *
from resources import load_font, load_image
from pygame.locals import *
import virtualdisplay

# screens.py
class QuitGame(Exception):
    """Exception to raise in update() to quit the game"""
    def __init__(self, value):
        """Create new QuitGame exception"""
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return repr(self.value)

class GameScreen(object):
    """Base class for AsteroidImpact game screens"""
    def __init__(self, screen, screenstack):
        """Initialize the base members of GameScreen"""
        self.screen = screen
        self.screenstack = screenstack
        self.opaque = True
        self.name = self.__class__.__name__

    def update(self, millis, logrowdetails, events):
        """Update the screen's game state"""
        pass

    def draw(self):
        """Draw the game screen to the physical screen buffer"""
        pass

class TextSprite(object):
    """Combines surface (bitmap) for text and drawing position to make drawing static text easier"""
    def __init__(self, textsurf, **kwargs):
        self.textsurf = textsurf
        self.textrect = self.textsurf.get_rect(**kwargs)
    def draw(self, screen):
        screen.blit(self.textsurf, self.textrect)

class BlackScreen(GameScreen):
    """
    Black screen. Shown to the player while other things are happening in other parts of
    the research
    """
    def __init__(self, screen, gamescreenstack):
        GameScreen.__init__(self, screen, gamescreenstack)
        self.name = 'black'
        self.opaque = True
        self.screenarea = self.screen.get_rect()

        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

    def draw(self):
        # draw background
        self.screen.blit(self.background, (0, 0))

class AsteroidImpactInstructionsScreen(GameScreen):
    def __init__(self, screen, gamescreenstack, click_to_continue=True):
        GameScreen.__init__(self, screen, gamescreenstack)
        self.click_to_continue = click_to_continue
        self.name = 'instructions'
        self.opaque = True
        self.screenarea = self.screen.get_rect()

        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250, 250, 250))

        self.textsprites = []
        self.sprites = pygame.sprite.Group()

        self.font_big = load_font('freesansbold.ttf', 36)
        red = (250, 10, 10)
        black = (10, 10, 10)
        self.font = load_font('freesansbold.ttf', 16)
        self.textsprites.append(
            TextSprite(self.font_big.render("How to Play", 1, red),
                       centerx=self.screenarea.width/2, top=0))

        s = Cursor()
        s.rect.topleft = (60, 60)
        self.sprites.add(s)
        self.textsprites.append(
            TextSprite(self.font.render(
                "Move your ship around with your mouse, picking up crystals", 1, black),
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
        asteroidscreenbounds = pygame.Rect(60, 200, 480-60-60, 80)
        asteroidgamebounds = virtualdisplay.gamerect_from_screenrect(asteroidscreenbounds)
        self.asteroids = pygame.sprite.Group([
            Asteroid(diameter=64,
                     dx=1.5,
                     dy=1.0,
                     top=asteroidgamebounds.top,
                     left=asteroidgamebounds.left,
                     area=asteroidgamebounds),
            Asteroid(diameter=80,
                     dx=2.5,
                     dy=-1,
                     top=asteroidgamebounds.top + 20,
                     left=asteroidgamebounds.left + 400,
                     area=asteroidgamebounds),
            Asteroid(diameter=40,
                     dx=-1,
                     dy=-3,
                     top=asteroidgamebounds.top + 40,
                     left=asteroidgamebounds.left + 600,
                     area=asteroidgamebounds)])
        self.textsprites.append(
            TextSprite(
                self.font.render(
                    "Avoid the bouncing asteroids. Hit one and it's game over.",
                    1, black),
                left=120, top=180))

        s = ShieldPowerup()
        s.rect.topleft = (60, 300)
        self.sprites.add(s)
        self.textsprites.append(TextSprite(
            self.font.render(
                "Pick up a shield to pass through asteroids for a few seconds",
                1, black),
            left=120, top=300))

        s = SlowPowerup()
        s.rect.topleft = (60, 360)
        self.sprites.add(s)
        self.textsprites.append(TextSprite(
            self.font.render(
                "Pick up a clock to slow asteroids for a few seconds",
                1, black),
            left=120, top=360))

        if self.click_to_continue:
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

    def update(self, millis, logrowdetails, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.click_to_continue:
                    # position cursor at the center
                    pygame.mouse.set_pos([self.screenarea.centerx, self.screenarea.centery])
                    # end the instructions screen:
                    self.screenstack.pop()
                    # game.py will switch to gameplay
            elif event.type is MOUSEBUTTONUP:
                pass

        # update asteroid positions
        for asteroid in self.asteroids:
            asteroid.update(millis)

class LevelCompletedOverlayScreen(GameScreen):
    def __init__(self, screen, gamescreenstack):
        GameScreen.__init__(self, screen, gamescreenstack)
        self.name = 'level_complete'
        self.opaque = False
        self.screenarea = self.screen.get_rect()
        self.font = load_font('freesansbold.ttf', 36)
        self.text = self.font.render("Level Completed", 1, (250, 10, 10))
        self.textpos = self.text.get_rect(
            centerx=self.screenarea.width/2, centery=self.screenarea.height/2)
        self.elapsedmillis = 0

    def draw(self):
        self.screen.blit(self.text, self.textpos)

    def close(self):
        if (len(self.screenstack) > 1
                and isinstance(self.screenstack[-2], AsteroidImpactGameplayScreen)):
            # advance to next level
            self.screenstack[-2].advance_level()
        # remove 'level completed' screen
        self.screenstack.pop()

    def update(self, millis, logrowdetails, events):
        self.elapsedmillis += millis

        if self.elapsedmillis >= 1000:
            self.close()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                #self.close()
                pass
            elif event.type is MOUSEBUTTONUP:
                pass

class GameOverOverlayScreen(GameScreen):
    def __init__(self, screen, gamescreenstack):
        GameScreen.__init__(self, screen, gamescreenstack)
        self.name = 'game_over'
        self.opaque = False
        self.screenarea = self.screen.get_rect()
        self.font = load_font('freesansbold.ttf', 36)
        self.text = self.font.render("You Died!", 1, (250, 10, 10))
        self.textpos = self.text.get_rect(
            centerx=self.screenarea.width/2, centery=self.screenarea.height/2)
        self.elapsedmillis = 0

    def draw(self):
        self.screen.blit(self.text, self.textpos)
        pass

    def close(self):
        if (len(self.screenstack) > 1
                and isinstance(self.screenstack[-2], AsteroidImpactGameplayScreen)):
            # reload same level
            self.screenstack[-2].setup_level()
        # remove 'game over' screen
        self.screenstack.pop()

    def update(self, millis, logrowdetails, events):
        self.elapsedmillis += millis

        if self.elapsedmillis >= 1000:
            self.close()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                pass
                #self.close()
            elif event.type is MOUSEBUTTONUP:
                pass


def circularspritesoverlap(a, b):
    x1 = a.gamerect.centerx
    y1 = a.gamerect.centery
    d1 = a.gamerect.width
    x2 = b.gamerect.centerx
    y2 = b.gamerect.centery
    d2 = b.gamerect.width
    # x1, y1, d1, x2, y2, d2
    return ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)) < (.25*(d1 + d2)*(d1 + d2))

def make_powerup(powerup_dict):
    # copy so that removing 'type' doesn't change original
    powerup_dict = dict(powerup_dict)
    powerup_type = powerup_dict.pop('type')
    if powerup_type == 'shield':
        return ShieldPowerup(**powerup_dict)
    if powerup_type == 'slow':
        return SlowPowerup(**powerup_dict)
    if powerup_type == 'none':
        return NonePowerup(**powerup_dict)
    print 'ERROR: Unknown type of powerup in level: ', powerup_type

class AsteroidImpactGameplayScreen(GameScreen):
    def __init__(self, screen, screenstack, levellist):
        GameScreen.__init__(self, screen, screenstack)
        self.name = 'gameplay'
        self.blackbackground = pygame.Surface(self.screen.get_size())
        self.blackbackground = self.blackbackground.convert()
        self.blackbackground.fill((0, 0, 0))

        self.gamebackground = load_image('background4x3.jpg', size=virtualdisplay.screenarea.size)
        # draw gamebackground on blackbackground to only have to draw black/game once per frame:
        self.blackbackground.blit(self.gamebackground, virtualdisplay.screenarea.topleft)

        self.statusfont = load_font('freesansbold.ttf', 36)
        self.statustext = self.statusfont.render('Placeholder Art', 1, (10, 10, 10))
        self.statustextrect = self.statustext.get_rect(
            centerx=virtualdisplay.screenarea.centerx,
            top=virtualdisplay.screenarea.top)

        self.noticefont = load_font('freesansbold.ttf', 36)
        self.noticetext = self.statusfont.render('[]', 1, (250, 10, 10))
        self.noticetextrect = self.statustext.get_rect(
            centerx=virtualdisplay.screenarea.centerx,
            centery=virtualdisplay.screenarea.centery)

        self.sound_death = load_sound('DeathFlash.wav')

        #Display The Background
        self.screen.blit(self.blackbackground, (0, 0))
        self.level_list = levellist
        if len(self.level_list) == 0:
            print 'ERROR: Level list is empty'
            raise QuitGame
        self.level_index = 0
        self.level_attempt = -1
        self.setup_level()

    def setup_level(self):
        leveldetails = self.level_list[self.level_index]
        self.level_millis = -2000 # for the 'get ready' and level countdown

        self.cursor = Cursor()
        self.target_positions = leveldetails['target_positions']
        self.target_index = 0
        self.target = Target(
            diameter=32,
            left=self.target_positions[0][0],
            top=self.target_positions[0][1])
        self.asteroids = [Asteroid(**d) for d in leveldetails['asteroids']]
        self.powerup_list = [make_powerup(d) for d in leveldetails['powerup_list']]
        self.powerup = self.powerup_list[0]
        self.next_powerup_list_index = 1 % len(self.powerup_list)
        self.mostsprites = pygame.sprite.OrderedUpdates(
            self.asteroids + [self.cursor, self.target])
        self.powerupsprites = pygame.sprite.Group()
        if self.powerup.image:
            self.powerupsprites.add(self.powerup)
        self.update_status_text()
        self.update_notice_text(self.level_millis, -10000)
        self.level_attempt += 1

    def advance_level(self):
        self.level_index = (self.level_index + 1) % len(self.level_list)
        self.level_attempt = -1
        self.setup_level()

    def update_status_text(self):
        """Update status text surfaces"""
        statusblurb = '%d/%d collected %2.2f seconds'%(
            self.target_index, len(self.target_positions), self.level_millis / 1000.)
        self.statustext = self.statusfont.render(statusblurb, 1, (10, 10, 10))
        self.statustextrect = self.statustext.get_rect(
            centerx=virtualdisplay.screenarea.centerx,
            top=virtualdisplay.screenarea.top)

    def update_notice_text(self, level_millis, oldlevel_millis):
        #                   Get Ready -
        # -1000... +1000    Go
        # -500 ... +500     Go
        # +500 ... death    [nothing]
        if oldlevel_millis < -2000 and -2000 <= level_millis:
            self.noticetext = self.noticefont.render('Get Ready', 1, (250, 10, 10))
            self.noticetextrect = self.noticetext.get_rect(
                centerx=virtualdisplay.screenarea.centerx,
                centery=virtualdisplay.screenarea.centery)
        if oldlevel_millis < -1000 and -1000 <= level_millis:
            self.noticetext = self.noticefont.render('Set', 1, (250, 10, 10))
            self.noticetextrect = self.noticetext.get_rect(
                centerx=virtualdisplay.screenarea.centerx,
                centery=virtualdisplay.screenarea.centery)
        if oldlevel_millis < 0 and 0 <= level_millis:
            self.noticetext = self.noticefont.render('Go', 1, (250, 10, 10))
            self.noticetextrect = self.noticetext.get_rect(
                centerx=virtualdisplay.screenarea.centerx,
                centery=virtualdisplay.screenarea.centery)
        if oldlevel_millis < 500 and 500 <= level_millis:
            self.noticetext = self.noticefont.render('', 1, (250, 10, 10))
            self.noticetextrect = self.noticetext.get_rect(
                centerx=virtualdisplay.screenarea.centerx,
                centery=virtualdisplay.screenarea.centery)

    def update(self, millis, logrowdetails, events):
        oldmlevelillis = self.level_millis
        self.level_millis += millis

        levelstate = 'countdown' if self.level_millis < 0 else 'playing'

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                pass
            elif event.type is MOUSEBUTTONUP:
                pass

        self.update_notice_text(self.level_millis, oldmlevelillis)
        if self.level_millis < 0:
            # get ready countdown
            # only update asteroids, cursor
            self.mostsprites.update(millis)
        else:
            # game is running (countdown to level start is over)
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
                self.next_powerup_list_index = \
                    (1 + self.next_powerup_list_index) % len(self.powerup_list)
                #print 'new available powerup is', self.powerup, 'at', self.powerup.gamerect
            self.powerup.update(millis)

            # Check target collision:
            if circularspritesoverlap(self.cursor, self.target):
                # hit.
                # todo: increment counter of targets hit
                self.target.pickedup()
                self.target_index += 1
                if self.target_index >= len(self.target_positions):
                    print 'completed level'
                    levelstate = 'completed'
                    self.screenstack.append(LevelCompletedOverlayScreen(
                        self.screen, self.screenstack))
                else:
                    # position for next crystal target:
                    self.target.gamerect.left = self.target_positions[self.target_index][0]
                    self.target.gamerect.top = self.target_positions[self.target_index][1]
                    self.target.update_rect()

            # Check powerup collision
            if self.powerup != None\
                and circularspritesoverlap(self.cursor, self.powerup)\
                and not self.powerup.active\
                and not self.powerup.used:
                print 'activating powerup:', self.powerup
                self.powerup.activate(self.cursor, self.asteroids)

            # Check asteroid collision:
            for asteroid in self.asteroids:
                if circularspritesoverlap(self.cursor, asteroid):
                    # todo: find a cleaner way to have the shield powerup do this work:
                    if not (self.powerup != None
                            and isinstance(self.powerup, ShieldPowerup)
                            and self.powerup.active):
                        self.sound_death.play()
                        print 'dead', self.cursor.rect.left, self.cursor.rect.top
                        levelstate = 'dead'
                        self.screenstack.append(
                            GameOverOverlayScreen(self.screen, self.screenstack))
                        break

        self.update_status_text()
        logrowdetails['level_millis'] = self.level_millis
        logrowdetails['level_number'] = self.level_index + 1
        logrowdetails['level_attempt'] = self.level_attempt + 1
        logrowdetails['level_state'] = levelstate

        logrowdetails['targets_collected'] = self.target_index
        logrowdetails['target_x'] = self.target.gamerect.centerx
        logrowdetails['target_y'] = self.target.gamerect.centery

        #active powerup (none, shield, slow)
        logrowdetails['active_powerup'] = 'none'
        if self.powerup and self.powerup.active:
            logrowdetails['active_powerup'] = self.powerup.type

        # on-screen powerup (these get weird when active)
        logrowdetails['powerup_x'] = self.powerup.gamerect.centerx
        logrowdetails['powerup_y'] = self.powerup.gamerect.centery
        logrowdetails['powerup_diameter'] = self.powerup.gamediameter
        logrowdetails['powerup_type'] = self.powerup.type

        logrowdetails['cursor_x'] = self.cursor.gamerect.centerx
        logrowdetails['cursor_y'] = self.cursor.gamerect.centery


    def draw(self):
        self.screen.blit(self.blackbackground, (0, 0))
        self.screen.blit(self.statustext, self.statustextrect)
        self.mostsprites.draw(self.screen)
        self.powerupsprites.draw(self.screen)
        self.screen.blit(self.noticetext, self.noticetextrect)

