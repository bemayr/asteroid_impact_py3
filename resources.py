# Asteroid Impact (c) by Nick Winters
# 
# Asteroid Impact is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
# 
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>. 
"""
Resource-loading utilities for AsteroidImpact
"""

from __future__ import absolute_import, division
import os, sys, pygame

# Changing these only takes effect on newly loaded sounds
# so set volume before any sounds are loaded
music_volume = 1.0
effects_volume = 1.0

image_cache = {}

def resource_path(filename):
    """
    Return transformed resource path.
    
    For example, a standalone single-exe build would need to move the 'data' folder references somewhere else.
    """
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

def load_image(name, size=None, convert_alpha=False, colorkey=None):
    """
    Load image, scaling to desired size if specified.
    
    Results are cached to make future loading of the same resource instant, but
    this means you shouldn't draw on returned surfaces.
    """
    # Look up image in cache
    cache_key = (name, size, convert_alpha, colorkey)
    if image_cache.has_key(cache_key):
        return image_cache[cache_key]
    
    if size == None:
        raise ValueError('please specify desired size')
    fullname = resource_path(os.path.join('data', name))
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message

    if convert_alpha:
        image = image.convert_alpha()
    elif colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.locals.RLEACCEL)
        image = image.convert()
    else:
        image = image.convert()

    if size != None:
        image = pygame.transform.smoothscale(image, size)

    # save in cache:
    image_cache[cache_key] = image

    return image

def load_sound(name):
    """
    Load audio clip from file name.
    """
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
    """
    Load music file from file name.
    """
    if not pygame.mixer or not pygame.mixer.get_init():
        return
    fullname = resource_path(os.path.join('data', name))
    try:
        pygame.mixer.music.load(fullname)
    except pygame.error, message:
        print 'Cannot load music:', fullname
        raise SystemExit, message

def mute_music():
    """Mute Music by setting volume to zero temporarily."""
    if not pygame.mixer or not pygame.mixer.get_init():
        return
    pygame.mixer.music.set_volume(0.0)

def unmute_music():
    """Restore music volume to configured music volume."""
    if not pygame.mixer or not pygame.mixer.get_init():
        return
    pygame.mixer.music.set_volume(music_volume)
