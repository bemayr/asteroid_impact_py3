from pygame import Rect
import random
from virtualdisplay import gamearea

SMALL_SIZES = [60, 100, 90, 70, 110, 80]
MEDIUM_SIZES = [110, 120, 150, 120, 140, 130]
LARGE_SIZES = [200, 160, 170, 220, 210, 220]
VARIED_SIZES = SMALL_SIZES + MEDIUM_SIZES + LARGE_SIZES

SLOW_SPEEDS = [4, 6, 6, 8]
MEDIUM_SPEEDS = [8, 12, 12, 14]
FAST_SPEEDS = [20, 24, 24, 28]
EXTREME_SPEEDS = [36, 40, 40, 44]

TARGET_SIZE = 32

def make_dir(speed, rnd):
	'Find dx,dy that work reasonably up to given speed. avoid dx=0 and dy=0'
	dx = rnd.randint(1, speed)
	dy = rnd.randint(1, speed)
	if rnd.randint(0,1) == 1:
		dx = -dx
	if rnd.randint(0,1) == 1:
		dy = -dy
	return (dx, dy)

def make_level(seed=None, num_targets=5, asteroid_count=3, asteroid_sizes=LARGE_SIZES, 
	asteroid_speeds=SLOW_SPEEDS, powerup_count=10, powerup_delay=1.0, powerup_types=['shield','slow']):
	rnd = random.Random(seed)
	level = {}
	target_positions = []
	for i in xrange(num_targets):
		target_positions.append((rnd.randint(0, gamearea.width - TARGET_SIZE), rnd.randint(0, gamearea.height - TARGET_SIZE)))
	level['target_positions'] = target_positions

	asteroids = []
	for i in xrange(asteroid_count):
		diameter = rnd.choice(asteroid_sizes)
		speed = rnd.choice(asteroid_speeds)
		dx,dy = make_dir(speed, rnd)
		asteroids.append(dict(
			diameter=diameter,dx=dx,dy=dy,
			top=(rnd.randint(0, gamearea.height - diameter)),
			left=(rnd.randint(0, gamearea.width - diameter))))
	level['asteroids'] = asteroids

	powerups = []
	if powerup_count > 0 and len(powerup_types) > 0:
		for i in xrange(powerup_count):
			powerup_left,powerup_top=(rnd.randint(0, gamearea.width - TARGET_SIZE), rnd.randint(0, gamearea.height - TARGET_SIZE))
			powerup_type = rnd.choice(powerup_types)
			powerups.append(dict(type=powerup_type,diameter=TARGET_SIZE,left=powerup_left,top=powerup_top))
			if powerup_delay > 0.0:
				powerups.append(dict(type='none', duration=powerup_delay))
	else:
		powerups = [dict(type='none',duration=1.0)]

	level['powerup_list'] = powerups

	return level

def get_levels():
	rnd = random.Random(3487437)
	# TODO: Don't depend on supplied screen area
	#gamearea = Rect(0,0,640,480)
	
	return [
		# very slow ramp up in basic difficulty with no powerups
		make_level(seed=29873487, num_targets=3, asteroid_count=1, asteroid_speeds=SLOW_SPEEDS, powerup_count=0),
		make_level(seed=49358743, num_targets=5, asteroid_count=1, asteroid_speeds=MEDIUM_SPEEDS, powerup_count=0),
		make_level(seed=23423453, num_targets=5, asteroid_count=2, asteroid_speeds=MEDIUM_SPEEDS, powerup_count=0),
		make_level(seed=34782342, num_targets=8, asteroid_count=3, asteroid_speeds=SLOW_SPEEDS, powerup_count=0),
		## introduce shield powerup
		make_level(seed=34782342, num_targets=8, asteroid_count=2, asteroid_speeds=MEDIUM_SPEEDS, 
			powerup_count=10, powerup_types=['shield'], powerup_delay=0.5),
		make_level(seed=34782342, num_targets=8, asteroid_count=3, asteroid_speeds=MEDIUM_SPEEDS, 
			powerup_count=10, powerup_types=['shield'], powerup_delay=0.5),
		## introduce slow powerup
		make_level(seed=239487234, num_targets=8, asteroid_count=3, asteroid_speeds=MEDIUM_SPEEDS, 
			powerup_count=10, powerup_types=['slow'], powerup_delay=0.5),
		make_level(seed=543245234, num_targets=10, asteroid_count=2, asteroid_speeds=FAST_SPEEDS, 
			powerup_count=10, powerup_types=['slow'], powerup_delay=0.5),

		# start mixing it up. These may get too difficult
		make_level(seed=134321432, num_targets=10, asteroid_count=4, asteroid_speeds=MEDIUM_SPEEDS, asteroid_sizes=MEDIUM_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),
		make_level(seed=234234234, num_targets=10, asteroid_count=4, asteroid_speeds=FAST_SPEEDS, asteroid_sizes=MEDIUM_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),
		make_level(seed=983746598, num_targets=10, asteroid_count=6, asteroid_speeds=MEDIUM_SPEEDS, asteroid_sizes=SMALL_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),
		make_level(seed=985623421, num_targets=10, asteroid_count=8, asteroid_speeds=MEDIUM_SPEEDS, asteroid_sizes=VARIED_SIZES,
			powerup_count=10, powerup_types=['slow','shield'], powerup_delay=2.0),

		# crazy town
		# beatable in 10.3s using shields continuously
		make_level(seed=34782342, num_targets=12, asteroid_count=5, asteroid_speeds=EXTREME_SPEEDS, 
			powerup_count=10, powerup_types=['shield'], powerup_delay=0.5),
		]
	
	
	return [
		dict(
			target_positions = [
				(rnd.randint(0, gamearea.width - TARGET_SIZE), rnd.randint(0, gamearea.height - TARGET_SIZE)),
				(rnd.randint(0, gamearea.width - TARGET_SIZE), rnd.randint(0, gamearea.height - TARGET_SIZE)),
				(rnd.randint(0, gamearea.width - TARGET_SIZE), rnd.randint(0, gamearea.height - TARGET_SIZE)),
				(rnd.randint(0, gamearea.width - TARGET_SIZE), rnd.randint(0, gamearea.height - TARGET_SIZE)),
				(rnd.randint(0, gamearea.width - TARGET_SIZE), rnd.randint(0, gamearea.height - TARGET_SIZE))],
			asteroids = [
				dict(diameter=100, dx=2, dy=5, top=100, left=10),
				dict(diameter=80, dx=4, dy=3, top=200, left=50),
				dict(diameter=60, dx=-5, dy=-3, top=120, left=400)],
			powerup_list = [
				dict(type='none',duration=1.0),
				dict(type='shield',diameter=TARGET_SIZE, left=rnd.randint(0, gamearea.width - TARGET_SIZE), top=rnd.randint(0, gamearea.height - TARGET_SIZE)),
				dict(type='none',duration=1.0),
				dict(type='slow',diameter=TARGET_SIZE, left=rnd.randint(0, gamearea.width - TARGET_SIZE), top=rnd.randint(0, gamearea.height - TARGET_SIZE)),
				dict(type='none',duration=1.0),
				dict(type='shield',diameter=TARGET_SIZE, left=rnd.randint(0, gamearea.width - TARGET_SIZE), top=rnd.randint(0, gamearea.height - TARGET_SIZE)),
				dict(type='none',duration=1.0),
				dict(type='slow',diameter=TARGET_SIZE, left=rnd.randint(0, gamearea.width - TARGET_SIZE), top=rnd.randint(0, gamearea.height - TARGET_SIZE)),
				dict(type='none',duration=1.0),
				dict(type='shield',diameter=TARGET_SIZE, left=rnd.randint(0, gamearea.width - TARGET_SIZE), top=rnd.randint(0, gamearea.height - TARGET_SIZE)),	
				dict(type='none',duration=1.0),
				dict(type='slow',diameter=TARGET_SIZE, left=rnd.randint(0, gamearea.width - TARGET_SIZE), top=rnd.randint(0, gamearea.height - TARGET_SIZE)),
				dict(type='none',duration=1.0),
				]
		),
		]
