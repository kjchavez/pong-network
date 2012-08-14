#Dummy Clients to test PongServer

import socket

host = "127.0.0.1"
port = 50001
s = []

for i in range(10):
	newSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	newSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	s.append(newSock)

