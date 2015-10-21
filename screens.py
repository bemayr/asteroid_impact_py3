# Asteroid Impact (c) by Nick Winters
# 
# Asteroid Impact is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
# 
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>. 
"""
Game screens for AsteroidImpact
"""

from sprites import *
from resources import load_font, load_image, mute_music, unmute_music
from pygame.locals import *
import virtualdisplay
import string

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
    """
    Sprite-like object for text that helps positioning text in game coordinates, and
    keeping text in position when text changes.
    """
    def __init__(self, font, text, color, **kwargs):
        """
        Create new TextSprite()
        
        Keyword arguments are transformed from game space to screen space and used to specify
        position of rasterized text.
        """
        self.font = font
        self.color = color
        self.text = None
        for arg in kwargs.keys():
            # convert some args from game coordinate space to screen coordinate space
            if arg == 'x' or arg == 'left' or arg == 'right' or arg == 'centerx':
                kwargs[arg] = virtualdisplay.screenpoint_from_gamepoint((kwargs[arg], 0))[0]
            elif arg == 'y' or arg == 'top' or arg == 'bottom' or arg == 'centery':
                kwargs[arg] = virtualdisplay.screenpoint_from_gamepoint((0, kwargs[arg]))[1]
            else:
                raise ValueError(
                    "TextSprite() doesn't implement support for rect keword arg '%s'" % arg)
        self.textsurf_get_rect_args = kwargs
        self.set_text(text)

    def set_text(self, text):
        """Set and render new text"""
        if text != self.text:
            self.text = text
            self.textsurf = self.font.render(self.text, 1, self.color)
            self.textrect = self.textsurf.get_rect(**self.textsurf_get_rect_args)

    def draw(self, screen):
        """Draw text on screen"""
        screen.blit(self.textsurf, self.textrect)

class BlackScreen(GameScreen):
    """
    Black screen. Shown to the player while other things are happening in other parts of
    the research. The player can't interact with the black sceen.
    """
    def __init__(self, screen, gamescreenstack):
        GameScreen.__init__(self, screen, gamescreenstack)
        self.name = 'black'
        self.opaque = True
        self.screenarea = self.screen.get_rect()

        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        self.first_update = True

    def update(self, millis, logrowdetails, events):
        if self.first_update:
            self.first_update = False
            # don't play music during the black screen
            mute_music()

    def draw(self):
        # draw background
        self.screen.blit(self.background, (0, 0))

def font_find_fitting_string_length(font, line, lineWidth):
    """return the length (in characters) of the string that fits within lineWidth"""
    for i in xrange(len(line), -1, -1):
        if font.size(line[0:i])[0] <= lineWidth:
            return i
    return len(line)


def valid_breakpoint_character(c):
    """return true when c is a valid word-wrapping breakpoint character"""
    # whitespace:
    return c in string.whitespace


class UserTextScreen(GameScreen):
    """
    Text Screen. Displays text specified in step.
    """
    def __init__(self, screen, gamescreenstack, click_to_continue=True, text="[No text value was specified]"):
        GameScreen.__init__(self, screen, gamescreenstack)
        self.click_to_continue = click_to_continue
        self.name = 'textdisplay'
        self.opaque = True
        self.blackbackground = pygame.Surface(self.screen.get_size())
        self.blackbackground = self.blackbackground.convert()
        self.blackbackground.fill((0, 0, 0))

        self.textsprites = []
        self.sprites = pygame.sprite.Group()

        big_font_size = virtualdisplay.screenrect_from_gamerect(
            pygame.Rect(0, 0, 72, 72)).height
        self.font_big = load_font('freesansbold.ttf', big_font_size)
        
        self.line_height = 36 # game-space like font size below
        small_font_size = virtualdisplay.screenrect_from_gamerect(
            pygame.Rect(0, 0, 32, 32)).height
        self.font = load_font('freesansbold.ttf', small_font_size)

        self.text_color = (250, 250, 250) # white

        self.init_text(text)

        if self.click_to_continue:
            self.textsprites.append(TextSprite(
                self.font_big, "Click To Begin", self.text_color,
                centerx=virtualdisplay.GAME_AREA.width/2,
                bottom=virtualdisplay.GAME_AREA.height))

        self.first_update = True
        
    def init_text(self, text):
        # wrap 'text' to fit in virtualdisplay.screen_width
        lines = text.split('\n')

        wrapped_lines = []
        for line in lines:
            line = line.strip()
            wrappedline = True
            while wrappedline:
                wrappedline = False

                maxlength = font_find_fitting_string_length(self.font, line, virtualdisplay.screenplayarea.width)
                if maxlength < len(line):
                    wrappedline = True
                    # find text breakpoint
                    breakpointlength = maxlength
                    while (breakpointlength > 0 and 
                           not valid_breakpoint_character(line[breakpointlength - 1])):
                        breakpointlength -= 1
                    if breakpointlength == 0:
                        # likely a long single word or URL. Just break where it fits
                        breakpointlength = maxlength
                    lineremainder = line[breakpointlength:]
                    line = line[:breakpointlength]

                wrapped_lines.append(line)

                if wrappedline:
                    # trim starting whitespace if any after line break
                    line = lineremainder.lstrip()

        # add text blocks, but vertically center them all on screen
        y = (virtualdisplay.GAME_AREA.height - (len(wrapped_lines) * self.line_height)) / 2
        for line in wrapped_lines:
            self.textsprites.append(
                TextSprite(self.font, line, self.text_color,
                           x=0,
                           y=y))
            y += self.line_height


    def draw(self):
        # draw background
        self.screen.blit(self.blackbackground, (0, 0))
        # draw all text blocks:
        for textsprite in self.textsprites:
            textsprite.draw(self.screen)

    def update(self, millis, logrowdetails, events):
        if self.first_update:
            self.first_update = False
            # don't play music:
            mute_music()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.click_to_continue:
                    # position cursor at the center
                    pygame.mouse.set_pos([
                        virtualdisplay.screenarea.centerx,
                        virtualdisplay.screenarea.centery])
                    # end the instructions screen:
                    self.screenstack.pop()
                    # game.py will switch to gameplay
            elif event.type is MOUSEBUTTONUP:
                pass

class AsteroidImpactInstructionsScreen(GameScreen):
    """
    Instructions Screen. Displays the game objects (ship, crystal, etc) and rules to the player.
    """
    def __init__(self, screen, gamescreenstack, click_to_continue=True):
        GameScreen.__init__(self, screen, gamescreenstack)
        self.click_to_continue = click_to_continue
        self.name = 'instructions'
        self.opaque = True
        self.blackbackground = pygame.Surface(self.screen.get_size())
        self.blackbackground = self.blackbackground.convert()
        self.blackbackground.fill((0, 0, 0))

        self.gamebackground = load_image('background4x3.jpg', size=virtualdisplay.screenarea.size)
        # draw gamebackground on blackbackground to only have to draw black/game once per frame:
        self.blackbackground.blit(self.gamebackground, virtualdisplay.screenarea.topleft)

        self.textsprites = []
        self.sprites = pygame.sprite.Group()

        big_font_size = virtualdisplay.screenrect_from_gamerect(
            pygame.Rect(0, 0, 72, 72)).height
        small_font_size = virtualdisplay.screenrect_from_gamerect(
            pygame.Rect(0, 0, 32, 32)).height
        self.font_big = load_font('freesansbold.ttf', big_font_size)
        red = (250, 250, 10)
        black = (255, 255, 255)
        self.font = load_font('freesansbold.ttf', small_font_size)
        self.textsprites.append(
            TextSprite(self.font_big, "How to Play", red,
                       centerx=virtualdisplay.GAME_AREA.width/2,
                       top=0))

        s = Cursor()
        s.gamerect.topleft = (120, 120)
        s.update_rect()
        self.sprites.add(s)
        self.textsprites.append(
            TextSprite(
                self.font,
                "Move your ship around with your mouse, picking up crystals",
                black, left=240, top=120))

        s = Target()
        s.gamerect.topleft = (120, 240)
        s.update_rect()
        self.sprites.add(s)
        self.textsprites.append(TextSprite(
            self.font, "Pick up all the crystals", black,
            left=240, top=240))

        s = Asteroid(diameter=32)
        s.gamerect.topleft = (120, 360)
        s.update_rect()
        self.sprites.add(s)
        asteroidgamebounds = pygame.Rect(120, 400, 960-120-120, 160)
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
                self.font,
                "Avoid the bouncing asteroids. Hit one and it's game over.",
                black, left=240, top=360))

        s = ShieldPowerup()
        s.gamerect.topleft = (120, 600)
        s.update_rect()
        self.sprites.add(s)
        self.textsprites.append(TextSprite(
            self.font,
            "Pick up a shield to pass through asteroids for a few seconds",
            black, left=240, top=600))

        s = SlowPowerup()
        s.gamerect.topleft = (120, 720)
        s.update_rect()
        self.sprites.add(s)
        self.textsprites.append(TextSprite(
            self.font,
            "Pick up a clock to slow asteroids for a few seconds",
            black, left=240, top=720))

        if self.click_to_continue:
            self.textsprites.append(TextSprite(
                self.font_big, "Click To Begin", red,
                centerx=virtualdisplay.GAME_AREA.width/2,
                bottom=virtualdisplay.GAME_AREA.height))

        self.first_update = True

    def draw(self):
        # draw background
        self.screen.blit(self.blackbackground, (0, 0))
        # draw all text blocks:
        for textsprite in self.textsprites:
            textsprite.draw(self.screen)
        self.sprites.draw(self.screen)
        self.asteroids.draw(self.screen)

    def update(self, millis, logrowdetails, events):
        if self.first_update:
            self.first_update = False
            # play music during the instructions at specified volume:
            unmute_music()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.click_to_continue:
                    # position cursor at the center
                    pygame.mouse.set_pos([
                        virtualdisplay.screenarea.centerx,
                        virtualdisplay.screenarea.centery])
                    # end the instructions screen:
                    self.screenstack.pop()
                    # game.py will switch to gameplay
            elif event.type is MOUSEBUTTONUP:
                pass

        # update asteroid positions
        for asteroid in self.asteroids:
            asteroid.update(millis)

class LevelCompletedOverlayScreen(GameScreen):
    """
    Show a "Level Complete" message on top of the gameplay screen, pausing the
    gameplay while this screen is visible.
    
    This screen automatically ends after a delay.
    """
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
        """Close this screen by removing it from the screen stack"""
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
    """
    Show a "Game Over" message on top of the gameplay screen, pausing the
    gameplay while this screen is visible.
    
    This screen automatically ends after a delay.
    """
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
        """Close this screen by removing it from the screen stack"""
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
    """
    Returns true if two circular game sprites overlap.
    
    The sprite overlap is checked using their ``gamerect`` to find the sprite position and diameter.
    """
    x1 = a.gamerect.centerx
    y1 = a.gamerect.centery
    d1 = a.gamerect.width
    x2 = b.gamerect.centerx
    y2 = b.gamerect.centery
    d2 = b.gamerect.width
    # x1, y1, d1, x2, y2, d2
    return ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)) < (.25*(d1 + d2)*(d1 + d2))

def make_powerup(powerup_dict):
    """
    returns a new powerup of the type specified in the level JSON by checking the ``"type"`` key in powerup_dict.
    """
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
    """
    Gameplay logic for the Asteroid Impact game.
    """
    def __init__(self, screen, screenstack, levellist):
        GameScreen.__init__(self, screen, screenstack)
        self.name = 'gameplay'
        self.blackbackground = pygame.Surface(self.screen.get_size())
        self.blackbackground = self.blackbackground.convert()
        self.blackbackground.fill((0, 0, 0))

        self.gamebackground = load_image('background4x3.jpg', size=virtualdisplay.screenarea.size)
        # draw gamebackground on blackbackground to only have to draw black/game once per frame:
        self.blackbackground.blit(self.gamebackground, virtualdisplay.screenarea.topleft)

        # draw outline around game area
        pygame.draw.rect(self.blackbackground, (250, 250, 250), virtualdisplay.screenplayarea, 1)

        status_font_size = virtualdisplay.screenrect_from_gamerect(
            pygame.Rect(0, 0, 64, 64)).height
        status_font = load_font('freesansbold.ttf', status_font_size)
        status_color = (250, 250, 10)

        notice_font_size = virtualdisplay.screenrect_from_gamerect(
            pygame.Rect(0, 0, 64, 64)).height
        notice_font = load_font('freesansbold.ttf', notice_font_size)
        notice_color = (250, 250, 10)

        self.status_asteroids_textsprite = TextSprite(
            status_font, "000/000", status_color,
            x=64,
            bottom=960)

        self.status_time_textsprite = TextSprite(
            status_font, "0.00s", status_color,
            x=virtualdisplay.GAME_AREA.width/2,
            bottom=960)

        self.notice_textsprite = TextSprite(
            notice_font, '', notice_color,
            centerx=virtualdisplay.GAME_AREA.centerx,
            centery=virtualdisplay.GAME_AREA.centery)

        self.textsprites = [
            self.status_asteroids_textsprite,
            self.status_time_textsprite,
            self.notice_textsprite]

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

        self.first_update = True

    def setup_level(self):
        """Setup for the current level"""
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
        """Advance the current level to the next in the list"""
        self.level_index = (self.level_index + 1) % len(self.level_list)
        self.level_attempt = -1
        self.setup_level()

    def update_status_text(self):
        """Update numbers in status text sprites"""
        self.status_asteroids_textsprite.set_text(
            '%d/%d collected'%(self.target_index, len(self.target_positions)))
        self.status_time_textsprite.set_text('%2.2f'%(self.level_millis / 1000.))

    def update_notice_text(self, level_millis, oldlevel_millis):
        """Update level countdown text"""
        #                   Get Ready -
        # -1000... -0000    Set
        # -0000 ... +500    Go
        # +500 ... death    [nothing]
        if oldlevel_millis < -2000 and -2000 <= level_millis:
            self.notice_textsprite.set_text('Get Ready')
        if oldlevel_millis < -1000 and -1000 <= level_millis:
            self.notice_textsprite.set_text('Set')
        if oldlevel_millis < 0 and 0 <= level_millis:
            self.notice_textsprite.set_text('Go')
        if oldlevel_millis < 500 and 500 <= level_millis:
            self.notice_textsprite.set_text('')

    def update(self, millis, logrowdetails, events):
        """Run per-frame game logic"""
        oldmlevelillis = self.level_millis
        self.level_millis += millis

        if self.first_update:
            self.first_update = False
            # play music during the instructions at specified volume:
            unmute_music()

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
        logrowdetails['level_name'] = self.level_list[self.level_index]['level_name']
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
        """draw game to ``self.screen``"""
        self.screen.blit(self.blackbackground, (0, 0))

        self.mostsprites.draw(self.screen)
        self.powerupsprites.draw(self.screen)

        # draw all text blocks:
        for textsprite in self.textsprites:
            textsprite.draw(self.screen)

