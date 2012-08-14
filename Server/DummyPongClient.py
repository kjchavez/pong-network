# Dummy Pong Server to test network programming
import socket

SERVERHOST = "127.0.0.1"
PLAYER1PORT = 50001
PLAYER2PORT = 50002
BUFFER_SIZE = 512

client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#client1.connect((SERVERHOST,PLAYER1PORT))
client1.sendto("ready",(SERVERHOST,PLAYER1PORT))
print client1.recv(BUFFER_SIZE)

client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#client2.connect((SERVERHOST,PLAYER2PORT))
client2.sendto("ready",(SERVERHOST,PLAYER2PORT))
print client2.recv(BUFFER_SIZE)

counter = 0

while True:
    print "Cycle #"+str(counter)
    counter += 1
    client1.sendto("1.0",(SERVERHOST,PLAYER1PORT))
    client2.sendto("2.0",(SERVERHOST,PLAYER2PORT))
    print "Server says to client 1:", client1.recv(BUFFER_SIZE)
    print "Server says to client 2:", client2.recv(BUFFER_SIZE)
    
