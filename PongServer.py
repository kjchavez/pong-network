# Pong Network Server
import socket
import select
from PongNetworkConstants import *


class PongServer(object):
    def __init__(self,host,port):
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((host,port))
        self.serverSocket.listen(5)
        
        self.descriptors = [self.serverSocket]
        print "PongServer started on port",port

        # Dictionary for easy access to games based on the player's socket
        self.games = {}
        self.gamesThatNeedPlayer = []

        self.ID = 1

    def run(self):
        while True:
            (readyToRead,readyToWrite,inError) = select.select(self.descriptors,[],[])

            # Iterate through all descriptors that are ready to be read
            for sock in readyToRead:

                if sock == self.serverSocket:
                    self.accept_new_connection()
                else:
                    self.games[sock].process(sock)

    def accept_new_connection(self):
        newSock, (foreignHost,foreignPort) = self.serverSocket.accept()
        self.descriptors.append(newSock)
        if self.gamesThatNeedPlayer:
            game = self.gamesThatNeedPlayer.pop()
            game.add_player(newSock,foreignHost,foreignPort)
            self.games[newSock] = game
        else:
            # Create a new game with the next available ID
            newGame = Game(self.ID,self)
            self.ID += 1
            # Add the newly connected user to the game
            newGame.add_player(newSock,foreignHost,foreignPort)
            # Set up appropriate references to the game
            self.games[newSock] = newGame
            self.gamesThatNeedPlayer.append(newGame)
        
            

class Game(object):
    def __init__(self, ID, server):
        self.ID = ID
        self.server = server

        self.paddle1PosY = PADDLE_START_Y
        self.paddle2PosY = PADDLE_START_Y

        self.player1 = None
        self.player2 = None

        # Flag indicating whether there are enough players connected
        self.enoughPlayers = False

    def add_player(self,playerSocket,foreignHost,foreignPort):
        if not self.player1:
            self.player1 = playerSocket
            self.player1.send(PLAYER1+EOT)
            print "Game %d added player %s:%s as Player 1" % (self.ID,foreignHost,foreignPort)
        elif not self.player2:
            self.player2 = playerSocket
            self.player2.send(PLAYER2+EOT)
            print "Game %d added player %s:%s as Player 2" % (self.ID,foreignHost,foreignPort)
            
        else:
            raise IOError("Tried to connect player to full game")

        if self.player1 and self.player2:
            self.enoughPlayers = True
            print "Game %d ready to begin!" % self.ID

    def process(self,player):
        # This try-except statement handles the case where a user forcibly
        # closes the pygame window
        try:
            message = player.recv(BUFFER_SIZE)
            # Message is an empty string, player has left
            if not message:
                self.disconnect_player(player)
                return
	    message = message.rstrip()
	    while (message[-1] != EOT):
		message += player.recv(BUFFER_SIZE)
	    message = message[:-1]
        except socket.error, errorMessage:
            self.disconnect_player(player)
            print errorMessage
            return



	# Clean up the message
	message = message.rstrip()
        
	# Message is asking whether there are enough players
        print message
        if message == POLL:
            if self.enoughPlayers:
                player.send(YES+EOT)
            else:
                player.send(NO+EOT)
            return
        
        # Otherwise the message is a position
        try:
            position = int(message)
        except:
            # Can't process request...
            print "Couldn't process request:",message
            
            return
        else:
            if player == self.player1:
                self.paddle1PosY = position
                #print "Player 1, Game %02d says: %s" % (self.ID,position)
                if self.player2: self.player2.send(message+EOT)
                return
            
            if player == self.player2:
                self.paddle2PosY = position
                #print "Player 2, Game %02d says: %s" % (self.ID,position)
                if self.player1: self.player1.send(message+EOT)
                return

            raise ValueError("Cannot process player for Game "+str(self.ID))

    def disconnect_player(self,player):
        if player not in (self.player1,self.player2):
            print "Player not found in Game",self.ID
            return False
        
        if player == self.player1:
            print "Player 1 has disconnected"
            self.player1 = None
            if self.player2:
                self.player2.send(DISCONNECTED)

        if player == self.player2:
            print "Player 2 has disconnected"
            self.player2 = None
            if self.player1:
                self.player1.send(DISCONNECTED)

        # Close the socket
        player.close()
        # Remove it from the list of sockets that the server is listening to
        self.server.descriptors.remove(player)
        # If this game is in gamesThatNeedPlayer, then the only player just disconnected
        if self in self.server.gamesThatNeedPlayer:
            self.server.gamesThatNeedPlayer.remove(self)
        # Remove dictionary entry linking player to this game
        del self.server.games[player]

        # Delete socket
        del player

        self.enoughPlayers = False
        if not self.player1 and not self.player2:
            print "All players from Game %02d have disconnected" % self.ID
            
        return True


def main():
    pongServer = PongServer(HOST,PORT)
    pongServer.run()

if __name__ == "__main__":
    main()
        
