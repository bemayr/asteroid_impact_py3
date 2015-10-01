from __future__ import absolute_import, division
from pygame import Rect

# virtual game area is always the same "resolution" and aspect ratio
gamearea = Rect(0,0,640*2,480*2)

# screen area and transform may vary depending on screen window size
# so these values are changed in set_screensize() below
screenarea = gamearea.copy()

# screen_from_game:
s_f_g_w = 1.0
s_f_g_h = 1.0
s_f_g_x = 0.0
s_f_g_y = 0.0

# game_from_screen
g_f_s_w = 1.0
g_f_s_h = 1.0
g_f_s_x = 0.0
g_f_s_y = 0.0

def set_screensize(screensize):
	global screenarea
	global s_f_g_w, s_f_g_h, s_f_g_x, s_f_g_y
	global g_f_s_w, g_f_s_h, g_f_s_x, g_f_s_y

	'update rect and transformations to aspect-preserve fit game in center of window'
	# find screenarea rect
	# the rect in screen space that the game will take up
	# by doing an aspect preserve scale, and centering in the middle of the screen
	if screensize[0] / screensize[1] > gamearea.width / gamearea.height:
		# game uses full height of screen
		screenarea = Rect(0, 0, screensize[1]*gamearea.width/gamearea.height, screensize[1])
		screenarea.centerx = screensize[0]/2
	else:
		# game uses full width of screen
		screenarea = Rect(0, 0, screensize[0], screensize[0]*gamearea.height/gamearea.width)
		screenarea.centery = screensize[1]/2
	
	# screen_from_game:
	s_f_g_w = screenarea.width / gamearea.width
	s_f_g_h = screenarea.height / gamearea.height
	s_f_g_x = screenarea.x - gamearea.x * s_f_g_w
	s_f_g_y = screenarea.y - gamearea.y * s_f_g_h

	# game_from_screen
	g_f_s_w = gamearea.width / screenarea.width
	g_f_s_h = gamearea.height / screenarea.height
	g_f_s_x = gamearea.x - screenarea.x * g_f_s_w
	g_f_s_y = gamearea.y - screenarea.y * g_f_s_h


def screenrect_from_gamerect(gamerect):
	return Rect(
		s_f_g_x + gamerect.x * s_f_g_w,
		s_f_g_y + gamerect.y * s_f_g_h,
		gamerect.width * s_f_g_w,
		gamerect.height * s_f_g_h)

def gamerect_from_screenrect(screenrect):
	return Rect(
		g_f_s_x + screenrect.x * g_f_s_w,
		g_f_s_y + screenrect.y * g_f_s_h,
		screenrect.width * g_f_s_w,
		screenrect.height * g_f_s_h)

def gamepoint_from_screenpoint(point):
	return (
		g_f_s_x + point[0] * g_f_s_w, 
		g_f_s_y + point[1] * g_f_s_h)
	
