from pygame import Rect
import random

SMALL_SIZES = [30,50,45,35,55,40]
MEDIUM_SIZES = [55,60,75,60,70,65]
LARGE_SIZES = [100,80,85,110,105,110]
VARIED_SIZES = SMALL_SIZES + MEDIUM_SIZES + LARGE_SIZES

SLOW_SPEEDS = [2,3,3,4]
MEDIUM_SPEEDS = [4,6,6,7]
FAST_SPEEDS = [10,12,12,14]
EXTREME_SPEEDS = [18,20,20,22]

def make_dir(speed, rnd):
	'Find dx,dy that work reasonably up to given speed. avoid dx=0 and dy=0'
	dx = rnd.randint(1, speed)
	dy = rnd.randint(1, speed)
	if rnd.randint(0,1) == 1:
		dx = -dx
	if rnd.randint(0,1) == 1:
		dy = -dy
	return (dx, dy)

def make_level(screenarea, seed=None, num_targets=5, asteroid_count=3, asteroid_sizes=LARGE_SIZES, 
	asteroid_speeds=SLOW_SPEEDS, powerup_count=10, powerup_delay=1.0, powerup_types=['shield','slow']):
	rnd = random.Random(seed)
	level = {}
	target_positions = []
	for i in xrange(num_targets):
		target_positions.append((rnd.randint(0, screenarea.width - 16), rnd.randint(0, screenarea.height - 16)))
	level['target_positions'] = target_positions

	asteroids = []
	for i in xrange(asteroid_count):
		diameter = asteroid_sizes[rnd.randint(0,len(asteroid_sizes)-1)]
		speed = asteroid_speeds[rnd.randint(0,len(asteroid_speeds)-1)]
		dx,dy = make_dir(speed, rnd)
		asteroids.append(dict(
			diameter=diameter,dx=dx,dy=dy,
			top=(rnd.randint(0, screenarea.height - diameter)),
			left=(rnd.randint(0, screenarea.width - diameter))))
	level['asteroids'] = asteroids

	powerups = []
	if powerup_count > 0 and len(powerup_types) > 0:
		for i in xrange(powerup_count):
			powerup_left,powerup_top=(rnd.randint(0, screenarea.width - 16), rnd.randint(0, screenarea.height - 16))
			powerup_type = powerup_types[rnd.randint(0,len(powerup_types)-1)]
			powerups.append(dict(type=powerup_type,diameter=16,left=powerup_left,top=powerup_top))
			if powerup_delay > 0.0:
				powerups.append(dict(type='none', duration=powerup_delay))
	else:
		powerups = [dict(type='none',duration=1.0)]

	level['powerup_list'] = powerups

	return level

def get_levels(screenarea):
	rnd = random.Random(3487437)
	# TODO: Don't depend on supplied screen area
	#screenarea = Rect(0,0,640,480)
	
	return [
		# very slow ramp up in basic difficulty with no powerups
		make_level(screenarea, seed=29873487, num_targets=3, asteroid_count=1, asteroid_speeds=SLOW_SPEEDS, powerup_count=0),
		make_level(screenarea, seed=49358743, num_targets=3, asteroid_count=1, asteroid_speeds=MEDIUM_SPEEDS, powerup_count=0),
		make_level(screenarea, seed=23423453, num_targets=5, asteroid_count=2, asteroid_speeds=MEDIUM_SPEEDS, powerup_count=0),
		make_level(screenarea, seed=34782342, num_targets=8, asteroid_count=3, asteroid_speeds=SLOW_SPEEDS, powerup_count=0),
		## introduce shield powerup
		make_level(screenarea, seed=34782342, num_targets=8, asteroid_count=2, asteroid_speeds=MEDIUM_SPEEDS, 
			powerup_count=10, powerup_types=['shield'], powerup_delay=0.5),
		make_level(screenarea, seed=34782342, num_targets=8, asteroid_count=3, asteroid_speeds=MEDIUM_SPEEDS, 
			powerup_count=10, powerup_types=['shield'], powerup_delay=0.5),
		## introduce slow powerup
		make_level(screenarea, seed=239487234, num_targets=8, asteroid_count=3, asteroid_speeds=MEDIUM_SPEEDS, 
			powerup_count=10, powerup_types=['slow'], powerup_delay=0.5),
		make_level(screenarea, seed=543245234, num_targets=10, asteroid_count=2, asteroid_speeds=FAST_SPEEDS, 
			powerup_count=10, powerup_types=['slow'], powerup_delay=0.5),

		# start mixing it up. These may get too difficult
		make_level(screenarea, seed=134321432, num_targets=10, asteroid_count=4, asteroid_speeds=MEDIUM_SPEEDS, asteroid_sizes=MEDIUM_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),
		make_level(screenarea, seed=234234234, num_targets=10, asteroid_count=4, asteroid_speeds=FAST_SPEEDS, asteroid_sizes=MEDIUM_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),
		make_level(screenarea, seed=983746598, num_targets=10, asteroid_count=6, asteroid_speeds=MEDIUM_SPEEDS, asteroid_sizes=SMALL_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),
		make_level(screenarea, seed=985623421, num_targets=10, asteroid_count=8, asteroid_speeds=MEDIUM_SPEEDS, asteroid_sizes=VARIED_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),

		# crazy town
		# beatable in 10.3s using shields continuously
		make_level(screenarea, seed=34782342, num_targets=12, asteroid_count=5, asteroid_speeds=EXTREME_SPEEDS, 
			powerup_count=10, powerup_types=['shield'], powerup_delay=0.5),
		]
	
	
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
				dict(type='none',duration=1.0),
				dict(type='shield',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='none',duration=1.0),
				dict(type='slow',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='none',duration=1.0),
				dict(type='shield',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='none',duration=1.0),
				dict(type='slow',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='none',duration=1.0),
				dict(type='shield',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),	
				dict(type='none',duration=1.0),
				dict(type='slow',diameter=16, left=rnd.randint(0, screenarea.width - 16), top=rnd.randint(0, screenarea.height - 16)),
				dict(type='none',duration=1.0),
				]
		),
		]
