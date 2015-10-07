
from sets import Set
class AsteroidLogger:
	"""Game state logger for AsteroidImpact game"""
	def __init__(self):
		"""Create new AsteroidLogger"""
		# make output log file
		class NoneFile:
			def write(self, data): pass
		#self.logfile = open('/Users/nick/src/AsteroidImpact/test.csv','w')
		self.logfile = NoneFile()
		
		self.columns = [
			# milliseconds since application start
			'total_millis',
			# number of step in sequence, for example 1 for instructions then 2 for game
			'step_number',
			# milliseconds elapsed during this step. This resets to 0 on step change
			'step_millis',
			# topmost screen name. Changes when mode change, but also inside of a mode
			# such as the level complete and game over screen.
			# instructions, gameplay, level_complete
			'top_screen',
			# game timer in milliseconds playing this level. 
			# This starts negative for the countdown. Collisions and power-ups become active at 0
			'level_millis',
			# number of level in in list of levels for this game mode step
			# starts counting at 1
			'level_number',
			# 1 for first attempt at this level, incrementing on each failure of the same level
			'level_attempt',
			# countdown, playing, completed or dead
			'level_state', 
			# number of targets collected in this level
			'targets_collected', 
			# center position of current target
			'target_x',
			'target_y',
			# the currently active powerup
			'active_powerup',
			# on-screen powerup
			# these shouldn't be trusted while a powerup is active because
			# active power-ups move around. A shield follows on top of the cursor
			# and the slow powerup moves offscreen.
			'powerup_x',
			'powerup_y',
			'powerup_diameter',
			'powerup_type',

			'cursor_x',
			'cursor_y']

		self.columns_set = Set(self.columns)
		
		# write headers
		self.log({col:col for col in self.columns})
			
	def csv_escape(self, s):
		"""Return s escaped and quoted as needed to be in a comma-separated CSV"""
		if ',' in s:
			# quote value
			return '"%"'%s.replace('"','""')
		return s
		
	def log(self, rowdict):
		"""Save new log row for values in rowdict"""		
		for i, key in enumerate(self.columns):
			if (i > 0):
				self.logfile.write(',')
			if rowdict.has_key(key):
				self.logfile.write(self.csv_escape(str(rowdict[key])))
		self.logfile.write('\r\n')
		
		# validation: check for keys in rowdict that aren't in columns
		for key in rowdict.keys():
			if not key in self.columns_set:
				print 'key "%s" not in known list of columns. Not included in log'%key
