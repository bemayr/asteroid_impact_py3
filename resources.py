"""
Resource-loading utilities for AsteroidImpact
"""

from __future__ import absolute_import, division
import os, sys, pygame

# Changing these only takes effect on newly loaded sounds
# so set volume before any sounds are loaded
music_volume = 1.0
effects_volume = 1.0

def resource_path(filename):
    # The 'data' directory isn't in the same spot when pyinstaller creates a
    # standalone build packed exe:
    # (via http://irwinkwan.com/tag/pyinstaller/ )
    #if hasattr(sys, "_MEIPASS"):
    #	return os.path.join(sys._MEIPASS, filename)
    return os.path.join(filename)

#functions to create our resources
def load_font(name, size):
    'Load pygame font for specified filename, font size'
    fullname = resource_path(os.path.join('data', name))

    if pygame.font:
        return pygame.font.Font(fullname, size)

    class NoneFont:
        def __init__(self, filename, fontsize):
            self.fontsize = fontsize
        def render(self, text, antialias, color, background=None):
            'return no text on a new surface'
            s = pygame.Surface(self.size(text))
            s.fill(color)
            return s
        def size(self, text):
            'return size of text without font'
            return (self.fontsize*len(text)//4, self.fontsize)

    return NoneFont(fullname, size)

def load_image(name, colorkey=None):
    fullname = resource_path(os.path.join('data', name))
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
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
    fullname = resource_path(os.path.join('data', name))
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
    fullname = resource_path(os.path.join('data', name))
    try:
        pygame.mixer.music.load(fullname)
    except pygame.error, message:
        print 'Cannot load music:', fullname
        raise SystemExit, message
