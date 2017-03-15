from datetime import datetime, timedelta
from twilio.rest import TwilioRestClient
import urllib
import random

class TwilioCall:
	twilio_account = 'AC63b2b4a1152e1a45e192be647477d012'
	twilio_token = '678df6afd3fdc14b5207800232e5e5bd'

	url_base = "http://twimlets.com/menu?"

	message_str = "Hello, I'm calling from Lutkin Hall located at 700 University Place."\
		"The temperature here is currently %.0f degrees %s."\
		"Extreme temperature may damage sensitive musical instruments located here."\
		"Please attend to this urgent matter as soon as possible."\
		"You can hang up or press 1 if something isn't working correctly"

	sms_message_str = "Lutkin temp is %.0f degrees %s."\
		" Calls were placed to %s"

	
	voicemail_url_base = "http://twimlets.com/voicemail?"
	voicemail_email = "amakhlin@gmail.com"
	voicemail_prompt_str = "Please leave a message and a number or an email address to"\
		"provide feedback. Thank you."


	def __init__(self, makecalls=1):
		self.twilio_client = TwilioRestClient(self.twilio_account, self.twilio_token)
		self.makecalls = makecalls
		self.phone_list = ['+17737915623']
		self.sms_list = ['']

	def set_params(self, phone_list, sms_list):
		self.phone_list = phone_list
		self.sms_list = sms_list

	def send_sms(self, temp, duration_str):
		phone_list_str = ''.join(str(el)+' ' for el in self.phone_list)
		if not phone_list_str:
			phone_list_str = 'no one.'
		body = self.sms_message_str % (temp, duration_str, phone_list_str)

		print body
		if self.makecalls:
			for phone_number in self.sms_list:
				self.twilio_client.sms.messages.create(to=phone_number, from_='+18472324123',
						body = body)


	def call(self, temp, duration_str):
	
		voicemail_args = { 'Email' : self.voicemail_email,
						   'Message' : self.voicemail_prompt_str}

		voicemail_url = self.voicemail_url_base + urllib.urlencode(voicemail_args)

		msg_str = self.message_str % (temp, duration_str)

		menu_args = { 'Message' : msg_str,
					  'Options[1]' : voicemail_url}

		url = self.url_base + urllib.urlencode(menu_args)

		print url
		if self.makecalls: 
			
			# loop over phone_list and make calls
			for phone_number in self.phone_list:
				self.twilio_client.calls.create(to=phone_number, from_='+18472324123',
	                           	url=url)

if __name__ == "__main__":
	twilio_call = TwilioCall(makecalls=0)

	twilio_call.call(81.7, 'and has been below 68 degrees for 4 hours')