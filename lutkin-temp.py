#!/usr/bin/python

from time import sleep
from DS18B20 import DS18B20
from disp import Disp
from lpf import LPF
from uiserver import UIServer
from datetime import datetime, timedelta
from ftable import FTable
from twiliocall import TwilioCall
from tempmonitor import TempMonitor
from lutkinsched import LutkinSched
import os
import sys
import traceback

DEBUG = False

# make sure current directory corresponds to the location of the script (cron does not work without this)
script_dir = os.path.dirname(sys.argv[0])
os.chdir(script_dir)

# read in the error file from the previous run and upload it to a fusion table
try:
	with open('elog.txt','r') as f:
		e_str = f.read()
		e_str = e_str.replace('\'', '')
		e_str = e_str.replace('\"', '')
except Exception, e:
	pass
else:
	try:
		# init log fution table
		ft_log = FTable('1KsdUMd1Bo-bt_1k2I7MnmdKKJHhRvD2LL4eKItc', ['Timestamp', 'Temperature', 'State', 'Message'])
		tstamp = datetime.now().strftime('%m/%d/%y %I:%M:%S %p')
  		ft_log.rec((tstamp, '', 'ERROR', e_str))
  	except Exception, e:
  		pass
  	else:
  		os.remove('elog.txt')

def update_params(params, sched, tMonitor, twilio_call):
	# params is a dictionary
	print 'got params from params table:\n'
	print params
	weekdays_list_allowed = map(int, params['weekdays_list_allowed'].split(','))
	print weekdays_list_allowed
	sched.set_parameters(int(params['start_calls_hour']), int(params['end_calls_hour']),
							weekdays_list_allowed, int(params['repeat_call_delay']))
	tMonitor.set_params(float(params['cold_limit']), float(params['hot_limit']), int(params['alarm_delay']))
	if params['phone_list'] is u'':
		phone_list = []
	else:
		phone_list = params['phone_list'].split(',')
	if params['sms_list'] is u'':
		sms_list = []
	else:
		sms_list = params['sms_list'].split(',')
	twilio_call.set_params(phone_list, sms_list)

# everything else goes into this try block so we can capture the error trace to a file
try:
	if DEBUG is True:
		print '****DEBUG****'

	# init main temperature history fustion table
	ft_temp_hist = FTable('1yw5uVh4rrq7k_VCgwDJEKhyxw3UmweqAMgvhyWg', ['Timestamp', 'Temperature'])

	# init parameters fusion table
	ft_params = FTable('1jjmCTe_RjbQE3OYXJ5yUEcIjYPCUbETzuWIJP6o', ['Parameter', 'Value'])

	# init log fution table
	ft_log = FTable('1KsdUMd1Bo-bt_1k2I7MnmdKKJHhRvD2LL4eKItc', ['Timestamp', 'Temperature', 'State', 'Message'])

	# configure modules with behaviour parameters
	if DEBUG:
		# makecalls=0 - don't make calls
		twilio_call = TwilioCall(makecalls=0) 
		# adjust limits, 68,78, 
		# debug=1 means transition from AOK to HOT/COLD in 5 sec
		tMonitor = TempMonitor(cold_limit=50, hot_limit=100, debug=1) 
		# call_any_time=True, repeat_call_delta=timedelta(seconds=20) 
		# call on weekends, repeat every 20s
		# debug=1 means timedelta from parameters is ignored
		sched = LutkinSched(script_dir, datetime.now(), call_any_time=True, repeat_call_delta=timedelta(seconds=20), debug=True)	
	else:
		twilio_call = TwilioCall(makecalls=1)
		tMonitor = TempMonitor(cold_limit=50, hot_limit=100, debug=0)
		sched = LutkinSched(script_dir, datetime.now())

	# get updated parameters from parameter fusion table
	params = ft_params.get()
	update_params(params, sched, tMonitor, twilio_call)

	# configure temperature sensor (1-wire)
	tsensor = DS18B20('/sys/bus/w1/devices/28-00000452b747/w1_slave')
	# configure serial 7 segment display
	disp = Disp('/dev/ttyAMA0', 9600, 0.5)
	# start ui server: connect to it like this - nc 127.0.1.1 3000
	ui = UIServer(debug=False)
	ui.start()

	tempf = tsensor()
	# configure the low pass filter
	if tempf is not None:
		lpf = LPF(8, tempf)

	cmd = None

	while True:
		# read the sensor
		tempf = tsensor()

		# execute command
		if cmd is not None:
			tempf = cmd_temp	

		if tempf is not None:
			tempf_avg = lpf(tempf)
			
			temp_str = '%.1f' % tempf_avg

			state, status_str = tMonitor.update(tempf_avg)
			params = sched.run(tempf_avg, temp_str, state, status_str, ft_temp_hist, ft_log, ft_params, twilio_call)
			# if new params come in from the params table (on the same schedule as the temp history table update)
			if params is not None:
				update_params(params, sched, tMonitor, twilio_call)

			stat_str =  ('%.1f F ') % tempf + ('avg: %.1f F ') % tempf_avg + 'state: %s ' % state + str(datetime.now())
			print stat_str

		else:
			print 'error reading 1-wire'
			temp_str = '00.0'

		# show temperature on local led display
		disp.temp(temp_str)

		# parse the command
		c = ui.get_cmd()
		if c is not None:
			c = c.rstrip()
			print 'Command: %s' % c
			
			if c.startswith('set'):
				cmd = 'set'
				cmd_temp = float(c.split(" ")[1])
				lpf.reset(cmd_temp)
			elif c.startswith('clr'):
				cmd = None
				lpf.reset(tempf)
			elif c.startswith('stat'):
				ui.send_status(stat_str)

		sleep(1.0)

except:
	# handle exception by dumping it to a file; read and upload it to fusion tables on next start (via crontab)
	with open('elog.txt', 'w') as f:
		traceback.print_exc(file=f)
