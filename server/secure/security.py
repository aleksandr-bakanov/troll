import socket

cross = open('crossdomain.xml').read()

HOST = ''
PORT = 843
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(32)
while 1:
	conn, addr = s.accept()
	data = conn.recv(24)
	print 'Connected by', addr, data
	if not data:
		conn.close()
	else:
		conn.sendall(cross)
		conn.close()
