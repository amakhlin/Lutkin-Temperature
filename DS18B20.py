''' Interface for DS18B20, a 1-wire thermometer ic

	returns temperature in degF or None if the sensor can't be read tree times in a row
'''

class DS18B20:
	def __init__(self, path='/sys/bus/w1/devices/28-00000452b747/w1_slave'):
		self.path = path

	def read(self):
		with open(self.path) as f:
			text = f.read()

		lines =  text.split("\n")
		if lines[0].endswith('YES'):
			secondline = lines[1]
			temp_data = secondline.split(" ")[9]
			temp = float(temp_data[2:])
			temp = temp / 1000
			tempf = 9./5. * temp + 32

			return tempf

		else:
			return None	

	def __call__(self):
		for i in range(3):
			t = self.read()
			if t is not None:
				return t


if __name__ == "__main__":
	import time

	tsensor = DS18B20('/sys/bus/w1/devices/28-00000452b747/w1_slave')

	while True:
		print '%.1f F' % tsensor()
		time.sleep(1)