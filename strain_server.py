#import measure
import socket, time
host = '127.0.0.1'
port = 12335

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.bind((host, port))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)
#sensor = Measure()

while 1:
	data = conn.recv(24)
	if not data: break
	print(data)
	conn.send(b'1000') #sensor.get_raw_values())
