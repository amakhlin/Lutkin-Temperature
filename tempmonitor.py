from datetime import datetime, timedelta

class TempMonitor:
	# states: 'AOK', 'MAYBECOLD', 'MAYBEHOT', 'COLD', 'HOT'

	ALARMDELAY = timedelta(minutes=10)

	def __init__(self, cold_limit=68, hot_limit=78, debug=0):
		
		self.COLDLIMIT = cold_limit
		self.HOTLIMIT = hot_limit

		self.s = 'AOK'
		self.debug = debug
		if self.debug:
			self.ALARMDELAY = timedelta(seconds=5)

	def set_params(self, cold_limit, hot_limit, alarm_delay):
		self.COLODLIMIT = cold_limit;
		self.HOTLIMIT = hot_limit;
		if not self.debug:
			self.ALARMDELAY = timedelta(minutes=alarm_delay)

	def update(self, temp):
		if self.s == 'AOK':
			if temp > self.HOTLIMIT:
				self.s = 'MAYBEHOT'
				self.mark = datetime.now()

			if temp < self.COLDLIMIT:
				self.s = 'MAYBECOLD'
				self.mark = datetime.now()

		if self.s == 'MAYBEHOT':
			if temp > self.HOTLIMIT:
				if (datetime.now() - self.mark) > self.ALARMDELAY:
					self.s = 'HOT'
					#self.mark = datetime.now()
			else:
				self.s = 'AOK'

		if self.s == 'MAYBECOLD':
			if temp < self.COLDLIMIT:
				if (datetime.now() - self.mark) > self.ALARMDELAY:
					self.s = 'COLD'
					#self.mark = datetime.now()
			else:
				self.s = 'AOK'

		if self.s == 'HOT':
			if temp < self.HOTLIMIT:
				self.s = 'AOK'

		if self.s == 'COLD':
			if temp > self.COLDLIMIT:
				self.s = 'AOK'

		return self.s, self.status()

	def status(self):
		str = ''
		if self.s == 'COLD':
			td_str = self.get_timedelta_str(datetime.now() - self.mark)
			str = 'and has been below %.0f %s' % (self.COLDLIMIT, td_str)
		elif self.s == 'HOT':
			td_str = self.get_timedelta_str(datetime.now() - self.mark)
			str = 'and has been above %.0f %s' % (self.HOTLIMIT, td_str)

		return str

	def get_timedelta_str(self, td):
		days = td.days
		hours = td.seconds / 3600
		minutes = td.seconds / 60

		td_str = ''

		days_str = ''
		if days > 0:
			if days > 1:
				days_str = '%d days' % days
			else:
				days_str = '1 day'
			td_str += days_str

		hours_str = ''
		if hours > 0:
			if hours > 1:
				hours_str = '%d hours' % hours
			else:
				hour_str = '1 hour'
			if not td_str:
				td_str+=hours_str

		minutes_str = ''
		if minutes > 0:
			if minutes > 1:
				minutes_str = '%d minutes' % minutes
			else:
				minutes_str = '1 minute'
			if not td_str:
				td_str+=minutes_str

		if self.debug:
			if td.seconds > 0:
				if td.seconds > 1:
					seconds_str = '%d seconds' % td.seconds
				else:
					seconds_str = '1 second'
				if not td_str:
					td_str+=seconds_str

		if td_str:
			td_str = 'for ' + td_str 
		return td_str

if __name__ == "__main__":
	from time import sleep

	tMon = TempMonitor(debug=1)

	#print tMon.get_timedelta_str(timedelta(minutes = 121))

	i = 0
	
	while True:
		i += 1

		if i < 5:
			t = 72.5
		if i > 5 and i < 15:
			t = 65.5
		if i > 15 and i < 25:
			t = 70.1
		if i > 25 and i < 35:
			t = 80.3
		if i > 35 and i < 45:
			t = 72.5
		if i > 45:
			exit()

		print t, tMon.update(t)
		sleep(1)