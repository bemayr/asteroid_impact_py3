from __future__ import absolute_import, division
from pygame import Rect

# virtual game area is always the same "resolution" and aspect ratio
gamearea = Rect(0,0,640*2,480*2)

# screen area and transform may vary depending on screen window size
# TODO: make that happen
screenarea = Rect(50,50,640,480)

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
	
