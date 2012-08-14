# Constants for the Pong Server-Client protocol

BUFFER_SIZE = 512
HOST = "10.30.32.54"
PORT = 50001

# Game Constants
BALL_START_VEL  = (1.,1.) 
PADDLE_START_Y  = 300
LEFT            = 1
RIGHT           = 2
TOP             = 3
BOTTOM          = 4
WINNING_SCORE   = 7
PLAYER          = 10
OPPONENT        = 11


#Packets (512 character limit, but shoot for 4 characters)
POLL = "poll"
YES = "yes"
NO = "no"
DISCONNECTED = "disc"
PLAYER1 = "player1"
PLAYER2 = "player2"
