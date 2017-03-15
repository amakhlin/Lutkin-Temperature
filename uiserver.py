import threading
import socket

'''
connect like this, ssh into pi first:
> sudo nc 127.0.1.1 3000

commands:
	set 77.4 - sets the temperature
	clr		 - clears perviously set temperature
'''

class UIServer(threading.Thread):
	def __init__(self, debug = False):
		threading.Thread.__init__(self)
		self.cmd = None
		self.debug = debug
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind((socket.gethostbyname(socket.gethostname()), 3000))
		if self.debug:
			print socket.gethostbyname(socket.gethostname())
		self.s.listen(5)
		self.daemon = True
		self.accepted = False

	def print_help(self):
		h_str = 'set 77.4 - sets the temperature\n'\
				'clr      - clear previously set temperature\n'\
				'stat     - print status info\n\n'

		return h_str

	def run(self, debug = False):
		if self.debug:
			print 'ui running'
		while True:
			self.accepted = False
			if self.debug:
				print 'about to accept'
			(self.cs, addr) = self.s.accept()
			self.accepted = True
			self.cs.sendall(self.print_help())
			if self.debug:
				print 'accepted!'

			while True:
				self.cmd = self.cs.recv(50)
				if len(self.cmd) == 0:
					break
				if self.cmd.startswith('\n'):
					self.cs.sendall(self.print_help())
					self.cmd = None
				if self.debug:
					print 'received', self.cmd

	def send_status(self, str):
		if self.accepted:
			self.cs.sendall(str)

	def get_cmd(self):
		cmd = self.cmd
		self.cmd = None

		return cmd


if __name__ == "__main__":
	server = UIServer(debug = True)
	server.start()
	while True:
		pass
