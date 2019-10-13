import socket

host = 'raspberrypi.local'
port = 12335


class StrainData:
	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.s.connect((host, port))

	def read_data(self):
		self.s.send(b'100')
		return self.s.recv(24)

#if __name__ == "__main__":
# datarecv = strain_data()
# while 1:
#	time.sleep(0.01)
#	print(datarecv.read_data())
