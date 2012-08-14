# Pong Client
import socket
from PongNetworkConstants import *
from GameEngine2D import *

USE_NETWORK = True

class PongWorld(World):
    def __init__(self,surface):
        World.__init__(self,"Pong",surface)
        self.playerScore = 0
        self.opponentScore = 0
        self.playerSide = None
        self.messageTimer = 0

    def set_side(self,side):
        self.playerSide = side
        
    def award_point(self,side):
        print "called award_point"
        if side == self.playerSide:
            print "point for player"
            self.playerScore += 1
            if self.playerScore >= WINNING_SCORE:
                self.winner = True
                self.end_game()
            else:
                self.reset()
                
        else:
            print "point for opponent"
            self.opponentScore += 1
            if self.opponentScore >= WINNING_SCORE:
                self.winner = False
                self.end_game()
            else:
                self.reset()

    def reset(self):
        ball = self.get_group("Ball")[0]
        ball.move_to(self.size/2)
        
    def display_message(self,message,time=1000,pause=True):
        print message

    def end_game(self):
        if self.winner:
            self.display_message("You Win!")
        else:
            self.display_message("You Lose!")
        
        pygame.event.post(pygame.event.Event(QUIT,{}))


class MessageWriter(Entity):
    def __init__(self,world,position=(200,200)):
        self.world = world
        self.type = "Message"
        self.image = None
        self.size = np.array(0,0) if not self.image else np.array(self.image.get_size())
        self.position = np.array(position)
        self.rect = pygame.Rect(self.position-self.size/2,self.size)

        self.timer = 0.
        self.message = ""

    def process(self,dt):
        if self.timer > 0:
            self.timer -= dt

    def erase(self):
        pass

    def render(self,dt):
        pass

    
class Ball(GraphicEntity):
    def __init__(self,world,position=(0,0),velocity=(200,200),size=30,color='red'):
        self.world = world
        self.position = np.array(position,float)
        self.velocity = np.array(velocity ,float)
        self.size = size
        self.type = "Ball"

        self.rect = pygame.Rect(self.position-(size/2,size/2),(size+1,size+1))

        # Color can also be passed in as any string that pygame recognizes as a color
        if isinstance(color,str):
            color = pygame.Color(color)
            

        # Create image
        self.image = pygame.surface.Surface((size+1,size+1))
        self.image.fill(pygame.Color('white'))
        pygame.draw.circle(self.image,color,(size/2,size/2),size/2)
        self.image.set_colorkey(self.image.get_at((0,0)))

        # Other Internal variables
        self.horizontalCollisionTimer = 0
        self.verticalCollisionTimer = 0

    def render(self,surface):
        surface.blit(self.image,self.position-np.array(self.image.get_size())/2)

    def erase(self):
        self.world.surface.blit(self.world.background,self.rect,self.rect)

    def process(self,dt):
        if self.world.isPaused:
            return
        
        # Check collisions
        self.has_hit_vertical()
        sideHit = self.has_hit_horizontal()

        if sideHit == RIGHT:
            self.world.award_point(LEFT)
        elif sideHit == LEFT:
            self.world.award_point(RIGHT)
        
        self.check_collisions()

        self.position += self.velocity * dt

        # Unless there's a real advantage to numpy, may just use Rects
        self.rect.center = self.position

    def check_collisions(self):
        # Simple version
        collisionPoints = [self.rect.midtop,self.rect.midright,self.rect.midbottom,self.rect.midleft]
        for entity in self.world.get_group("Paddle"):
            for point in collisionPoints:
                if entity.collides_with(point):
                    if point == self.rect.midleft:
                        self.velocity[0] = abs(self.velocity[0])
                    elif point == self.rect.midright:
                        self.velocity[0] = -abs(self.velocity[0])
                    elif point == self.rect.midtop:
                        self.velocity[1] = -abs(self.velocity[1])
                    elif point == self.rect.midbottom:
                        self.velocity[1] = abs(self.velocity[1])

    def collides_with(self,point):
        if LA.norm(point-self.position) < self.size/2:
            return True
        return False

    def has_hit_horizontal(self):
        if (self.position[0] > self.world.get_width() - self.size/2):
            self.velocity[0] = -abs(self.velocity[0])
            return RIGHT
        if (self.position[0] < self.size/2):
            self.velocity[0] = abs(self.velocity[0])
            return LEFT

        return None

    def has_hit_vertical(self):
        if (self.position[1] > self.world.get_height() - self.size/2):
            self.velocity[1] = -abs(self.velocity[1])
            return BOTTOM
        if (self.position[1] < self.size/2):
            self.velocity[1] = abs(self.velocity[1])
            return TOP

        return None


class Paddle(GraphicEntity):
    def __init__(self,world,position=(0,0),velocity=(0,0),controller=PLAYER,size=(30,100),color='black'):
        self.world = world
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.size = np.array(size)
        self.controller = controller
        self.type = "Paddle"

        self.rect = pygame.Rect(self.position-self.size/2,self.size)
        
        # Color can also be passed in as any string that pygame recognizes as a color
        if isinstance(color,str):
            color = pygame.Color(color)
            
        self.image = pygame.surface.Surface(self.size)
        pygame.draw.rect(self.image,color,pygame.Rect((0,0),self.size))


    def render(self,surface):
        surface.blit(self.image,self.position-self.size/2)

    def erase(self):
        self.world.surface.blit(self.world.background,self.rect,self.rect)

    def process(self,dt):
        if self.world.isPaused:
            return
        
        if self.controller == PLAYER:
            # Only the Y coordinate can move, according to the mouse position
            self.move_to_y(pygame.mouse.get_pos()[1])
            
    def move_to(self,pos):
        self.position = np.array(pos)
        self.rect.center = self.position

    def move_to_y(self,y):
        self.position[1] = y
        self.rect.center = self.position

    def get_pos(self):
        return self.position

    def check_collisions(self):
        pass

    def collides_with(self,point):
        return self.rect.collidepoint(point)

class Score(GraphicEntity):
    def __init__(self,world,position,owner,color='black'):
        self.world = world
        self.position = np.array(position)
        self.owner = owner
        self.currentScore = -1
        self.color = color
        self.type = "Score"

        if isinstance(self.color,str):
            self.color = pygame.Color(self.color)
            
        self.font = pygame.font.Font(None,36)
        self.image = self.font.render(str(self.currentScore),True,self.color)
        self.size = np.array(self.image.get_size())
        self.rect = pygame.Rect(self.position - self.size/2, self.size)

    def render(self,surface):
        surface.blit(self.image,self.rect)

    def erase(self):
        self.world.surface.blit(self.world.background,self.rect,self.rect)

    def process(self,dt):
        if self.owner == PLAYER:
            newScore = self.world.playerScore
        else:
            newScore = self.world.opponentScore

        if newScore != self.currentScore:
            print "Change in score"
            self.currentScore = newScore
            self.update_image()

    def update_image(self):
        self.image = self.font.render(str(self.currentScore),True,self.color)
        self.size = np.array(self.image.get_size())
        self.rect = pygame.Rect(self.position - self.size/2,self.size)


class SocketEntity(Entity):
    def __init__(self,world,host,port):
        self.world = world
        self.host = host
        self.port = port
        self.type = "Socket"

        self.clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clientSocket.connect((host,port))

        self.hasNotRecv = True
        self.opponentConnected = False
            
    def get_data(self):
        self.hasNotRecv = False
        string = self.clientSocket.recv(BUFFER_SIZE)
        #print "Server says:",string
        return string

    def put_data(self,data):
        self.clientSocket.send(str(data))

    def process(self,dt):
        if self.opponentConnected:
            paddles = self.world.get_group("Paddle")
            for paddle in paddles:
                if paddle.controller == PLAYER:
                    self.put_data(paddle.get_pos()[1])
                elif paddle.controller == OPPONENT:
                    message = self.get_data()
                    
                    # Check if other player disconnected
                    if message == DISCONNECTED:
                        self.world.display_message("Opponent disconnected!")
                        self.opponentConnected = False
                        self.world.pause()
                        return

                    # Otherwise the message is a position
                    newY = int(message)
                    paddle.move_to_y(newY)
        else:
            # Ask the server if the other player is connected yet
            print "Asking if opponent is connected..."
            self.clientSocket.send(POLL)
            response = self.clientSocket.recv(BUFFER_SIZE)
            print "Server responded:",response
            if response == YES:
                self.opponentConnected = True
                self.world.unpause()
                

def main():
    pygame.init()
    screen = pygame.display.set_mode((400,600))
    screenWidth,screenHeight = screen.get_size()
    screenDimensions = np.array(screen.get_size())
    pygame.display.set_caption("Socket Pong")
    screen.fill((255,255,255))
    pygame.display.flip()

    # Game Objects
    world = PongWorld(screen)
    
    if USE_NETWORK:
        # Create SocketEntity first and receive client's player number
        sock = SocketEntity(world,HOST,PORT)
        world.add(sock)
        playerNumber = sock.get_data()
    
        print "This player designated as %s by the server." % playerNumber
        controllers = (PLAYER,OPPONENT) if (playerNumber == PLAYER1) else (OPPONENT,PLAYER)
        scores = controllers
        world.set_side(LEFT if playerNumber == PLAYER1 else RIGHT)
    else:
        # For testing purposes, mouse will control both paddles
        controllers = (PLAYER,PLAYER)
        scores = (PLAYER,OPPONENT)
        
        
    paddleLeft = Paddle(world,position=np.array([20,screenHeight/2]),controller=controllers[0])
    paddleRight = Paddle(world,position=np.array([screenWidth-20,screenHeight/2]),controller=controllers[1])
    ball = Ball(world,position=screenDimensions/2)

    scoreLeft = Score(world,(screenWidth/4,50),scores[0])
    scoreRight = Score(world,(3*screenWidth/4,50),scores[1])
    
    world.add(paddleLeft)
    world.add(scoreLeft)
    world.add(paddleRight)
    world.add(scoreRight)
    world.add(ball)

    if not USE_NETWORK:
        world.unpause()

    world.run_main_loop()
    pygame.quit()

if __name__ == "__main__":
    main()
    
