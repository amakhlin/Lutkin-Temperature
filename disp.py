'''Interface for a 7 digit serial display, communication is via the serial port

	call it like this:

	from disp import Disp

	disp = Disp()
	disp.temp('55.4')


'''

import serial

class Disp:
	def __init__(self, port='/dev/ttyAMA0', baud=9600, timeout=0.5):
		self.port = port
		self.baud = baud
		self.timeout = timeout
		self.act_ind = False
		self.s = serial.Serial(self.port, self.baud, timeout=self.timeout)
		self.write_byte(0x76)

	def write_str(self, str):
		self.s.write(str)

	def write_byte(self, byte):
		self.s.write(chr(byte))

	def ind(self, on):
		self.write_byte(0x77)

		if on:
			self.write_byte(0x5)
		else:
			self.write_byte(0x4)
	
	def activity_toggle(self):
		self.act_ind = not self.act_ind
		self.ind(self.act_ind)

	def temp(self,tempS):
		#set cursor to left most positoin
		self.write_byte(0x79)
		self.write_byte(0x0)

		#decode the number
		n = float(tempS)
		
		#delete decimal point
		mod_str = str(int(n*10))

		mod_str = ('%4s') % mod_str
		self.write_str(mod_str)

		#paint the decimal dot
		self.write_byte(0x77)
		self.write_byte(0x4)

		self.activity_toggle()

if __name__ == "__main__":
	import time
	#d = disp('/dev/ttyAMA0', 9600, 0.5)
	disp = Disp()

	for i in range(0,1500):
		disp.temp(str(float(i/10.)))
		time.sleep(.4)