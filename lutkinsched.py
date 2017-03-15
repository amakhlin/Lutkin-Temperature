from datetime import datetime, timedelta
from twiliocall import TwilioCall
from ftable import FTable

class LutkinSched:
	def __init__(self, script_dir, now, call_any_time=False, repeat_call_delta = timedelta(hours=4), debug=False):
		self.call_any_time = call_any_time
		self.repeat_call_delta = repeat_call_delta
		self.next_call_time = now
		self.call_scheduled = False

		self.ft_logable_delta = timedelta(minutes=15)
		self.next_ftable_time = now + self.ft_logable_delta		

		self.start_calls_hour = 9
		self.end_calls_hour = 17
		self.weekdays_list_allowed = [0,1,2,3,4]

		self.debug = debug
	
	def set_parameters(self, start_calls_hour, end_calls_hour, weekdays_list_allowed, repeat_call_delay):
		self.start_calls_hour = start_calls_hour
		self.end_calls_hour = end_calls_hour
		self.weekdays_list_allowed = weekdays_list_allowed
		if not self.debug:
			self.repeat_call_delta = timedelta(hours=repeat_call_delay)

	def run(self, temp, temp_str, state, status_str, ft_temp_hist, ft_log, ft_params, twilio_call):
		now = datetime.now()

		self.schedule_call(now, temp, state, status_str, twilio_call, ft_log)
		params = self.schedule_ftable_update(now, temp_str, ft_temp_hist, ft_params)

		return params

	def allowed_to_call(self, now):
		if self.call_any_time is True:
			return True
		else:
			return 	(now.hour >= self.start_calls_hour and 
					now.hour <=self.end_calls_hour and 
					now.weekday() in self.weekdays_list_allowed)

	def schedule_call(self, now, temp, state, status_str, twilio_call, ft_log):
		if state is 'COLD' or state is 'HOT':
			if not self.call_scheduled or (self.call_scheduled and now > self.next_call_time):
				if self.allowed_to_call(now):
					twilio_call.call(temp, status_str)
					twilio_call.send_sms(temp, status_str)
					self.next_call_time = now + self.repeat_call_delta
					self.call_scheduled = True
					# record the call in Lutkin Message Log fusion table
					
  					tstamp = now.strftime('%m/%d/%y %I:%M:%S %p')
  					ft_log.rec((tstamp, str(temp), state, status_str))
		else:
			self.call_scheduled = False			

	def schedule_ftable_update(self, now, temp_str, ft_temp_hist, ft_params):
		params = None

		if now > self.next_ftable_time:
			# record temperature in history table
			tstamp = datetime.now().strftime('%m/%d/%y %I:%M %p')
			ft_temp_hist.rec((tstamp, temp_str))
			self.next_ftable_time = now + self.ft_logable_delta

			# get updated parameters from the parameters table
			params = ft_params.get()

		return params