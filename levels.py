from pygame import Rect
import random

def get_levels(screenarea):
	rnd = random.Random(3487437)
	# TODO: Don't depend on supplied screen area
	#screenarea = Rect(0,0,640,480)
	
	return [
		dict(
			target_positions = [
				(rnd.randint(0, screenarea.width - 16), rnd.randint(0, screenarea.height - 16)),
				(rnd.randint(0, screenarea.width - 16), rnd.randint(0, screenarea.height - 16)),
				(rnd.randint(0, screenarea.width - 16), rnd.randint(0, screenarea.height - 16)),
				(rnd.randint(0, screenarea.width - 16), rnd.randint(0, screenarea.height - 16)),
				(rnd.randint(0, screenarea.width - 16), rnd.randint(0, screenarea.height - 16))],
			asteroids = [
				dict(diameter=100, dx=2, dy=5, top=100, left=10),
				dict(diameter=80, dx=4, dy=3, top=200, left=50),
				dict(diameter=60, dx=-5, dy=-3, top=120, left=400)],
			powerup_list = [
				dict(type='shield',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='slow',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='shield',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='slow',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='shield',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),	
				dict(type='slow',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				]
		),
		]
