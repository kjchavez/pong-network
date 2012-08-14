
import acm.graphics.*;

import acm.program.*;
import acm.util.*;

import java.applet.*;
import java.awt.*;
import java.awt.event.*;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.net.UnknownHostException;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class SimplePong extends GraphicsProgram {

	/** Width and height of application window in pixels */
	public static final int APPLICATION_WIDTH = 400;
	public static final int APPLICATION_HEIGHT = 600;

	/** Dimensions of game board (usually the same) */
	private static final int WIDTH = APPLICATION_WIDTH;
	private static final int HEIGHT = APPLICATION_HEIGHT;

	/** Game Difficulty (relative speed that ball appears to move at) */
	private static final double EASY = 10.0;
	private static final double MEDIUM = 8.0;
	private static final double HARD = 5.0;

	/** Audio Clip containing the sound of a "bounce" */
	AudioClip bounceClip = MediaTools.loadAudioClip("bounce.au");

	/** Random Generator */
	private RandomGenerator rgen = RandomGenerator.getInstance();


	/** Dimensions of the paddle */
	private static final int PADDLE_WIDTH = 10;
	private static final int PADDLE_HEIGHT = 60;

	/** More Specifics about the Paddles */
	private GRect paddle1 = new GRect  (PADDLE_X_OFFSET,HEIGHT/2 ,PADDLE_WIDTH, PADDLE_HEIGHT );
	private GRect paddle2 = new GRect  (WIDTH - PADDLE_X_OFFSET,HEIGHT/2 ,PADDLE_WIDTH, PADDLE_HEIGHT );

	/** Offset of the paddle up from the sides */
	private static final int PADDLE_X_OFFSET = 30;


	/** The Game Ball */
	private GOval ball = new GOval (2*BALL_RADIUS,2*BALL_RADIUS);

	/** The velocity of the ball in x and y components*/
	private double vx, vy;

	/** Radius of the ball in pixels */
	private static final int BALL_RADIUS = 10;

	/** Y Velocity Of Ball */
	private static final double YVEL = 3.0;

	/**Make this a variable that you get passed in by the server */
	private static String PLAYER;
	private static int LOCATION;
	public static Socket socket;

	private static  OutputStream socketOutput;
	private static  InputStream socketInput;
	private static int Y;

	/**Methods*/

	private void createPaddles (){
		paddle1.setFilled(true);
		paddle1.setColor(Color.BLACK);
		add (paddle1);
		paddle2.setFilled(true);
		paddle2.setColor(Color.BLACK);
		add (paddle2);
	}

	private void createBall() {
		ball.setFilled(true);
		ball.setColor(Color.DARK_GRAY);
		vy=-2;
		vx=-3;
		ball.setLocation(WIDTH/2-BALL_RADIUS, HEIGHT/2 -BALL_RADIUS);
		add (ball);

	}

	private void moveBall(int y) {
		String locReadCon = "";
		int n = 0;
		byte[] locRead = new byte[512];


		while (true) {
			paddleControl( LOCATION);

			if (ball.getX() >= (WIDTH - 2*BALL_RADIUS ) ) break; //
			if (ball.getX() <= (2*BALL_RADIUS)) break;
			checkCollision ();
			ball.move(vx, vy);

			if (ball.getY() < 0) {
				vy=-vy;
			}
			if (ball.getY() > HEIGHT - 2*BALL_RADIUS){
				vy=-vy;
			}
			pause(MEDIUM);


			if (PLAYER.equals("player1")){

				if (Y <= HEIGHT-(PADDLE_HEIGHT/2) && Y >= PADDLE_HEIGHT/2){
					paddle1.setLocation ( PADDLE_X_OFFSET , Y-PADDLE_HEIGHT/2);


					//we also have to continously write this location to the server
				}

			}else{
				if (Y <= HEIGHT-(PADDLE_HEIGHT/2) && Y >= PADDLE_HEIGHT/2){
					paddle2.setLocation ( PADDLE_X_OFFSET , Y-PADDLE_HEIGHT/2);
					try {
						socketOutput.write(Y);//not sure if it truncates after 255


					} catch (IOException ex) {
						// TODO Auto-generated catch block
						ex.printStackTrace();
					}

				}
			}

			try {
				//ByteBuffer loc = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN);
				//loc.putInt(e.getY());
				String yloc = "" + Y+ "!";
				byte[] loc = yloc.getBytes();
				socketOutput.write(loc);//not sure if it truncates after 255
				socketOutput.flush();

				while (locRead[n] != '!'){
					
					socketInput.read(locRead);

					locReadCon = locReadCon + locRead[n];
					n++;


				}
				LOCATION = Integer.parseInt(locReadCon);

			} catch (IOException ex) {
				// TODO Auto-generated catch block
				ex.printStackTrace();
			}






		}

	}

	private GObject getCollidingObject() {

		if (getElementAt(ball.getX(), ball.getY()) != null) {
			return getElementAt(ball.getX(), ball.getY());
		}
		else if 
		(getElementAt(ball.getX() + 2*BALL_RADIUS,ball.getY()) != null){
			return getElementAt(ball.getX() + 2*BALL_RADIUS,ball.getY());
		}
		else if
		(getElementAt(ball.getX() + 2*BALL_RADIUS,ball.getY()+ 2*BALL_RADIUS) != null){
			return getElementAt(ball.getX() + 2*BALL_RADIUS,ball.getY()+ 2*BALL_RADIUS);
		}
		else if 
		(getElementAt(ball.getX(),ball.getY()+2*BALL_RADIUS) != null){
			return getElementAt(ball.getX(),ball.getY()+2*BALL_RADIUS);
		} else 
			return null;
	}

	private void checkCollision() {
		GObject collider = getCollidingObject();
		if (collider == (paddle1 )) {
			vx =  Math.abs(vx);
			bounceClip.play();
		} 
		if (collider == (paddle2 )) {
			vx= - Math.abs(vx); 
			bounceClip.play();
		} 
		//what to say if collidder is null? I want to say nothing happnens

	}

	private void paddleControl( double location) {
		if (PLAYER.equals("player1")){
			paddle2.setLocation ( WIDTH - PADDLE_X_OFFSET , location-PADDLE_HEIGHT/2);

		}else {
			paddle1.setLocation ( PADDLE_X_OFFSET , location-PADDLE_HEIGHT/2);
		}
		//trying to communicate with server
	}

	private boolean playersReady() {
		String pollStr = new String("poll"+'!');//for output

		byte [] poll = pollStr.getBytes();//for output

		byte[] b = new byte[512]  ; //for input



		try {
			socketOutput.write(poll);
			socketOutput.flush();


			socketInput.read(b);

			String response = new String(b);
			System.out.print(response);
			System.out.print("\n");

			String x = response.substring(0,3);
			if (x.equals("yes")){
				return true;
			}else{
				System.out.print("false num 1");
				return false;

			}

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return false;
	}

	public void init () {
		byte[] player = new byte[512] ;

		try {
			socket = new Socket("10.30.32.54", 50001);
			socketOutput = socket.getOutputStream();
			socketInput = socket.getInputStream();
			System.out.print("try");

			int n = 0;
			String playerCon = "";
			int bytesRead = 0;
			
			do {
				
				bytesRead =  socketInput.read(player);

				for (int i = 0; i< bytesRead; i++){
					playerCon = playerCon + (char)player[i];
				}
				n += bytesRead;
			} while (playerCon.charAt(n-1) != '!');
			
			PLAYER = playerCon;
			
			
			System.out.print("Initial Player Designation");

		} catch (UnknownHostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			System.out.print("catch");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}


		createPaddles ();
		addMouseListeners ();
	}

	//Creates a mouse event that responds to a moving mouse. Center of paddle moves with mouse
	public void mouseMoved (MouseEvent e) {
		Y = e.getY();

	}

	public void run () {

		while(true) {


			if (playersReady()){
				System.out.print("Players are ready: true");
				while(true) {
					//countdown
					try {
						Thread.sleep(4000);
					} catch (InterruptedException ex) {
						// TODO Auto-generated catch block
						ex.printStackTrace();
					} 


					createBall ();
					moveBall(Y);
					remove (ball); //What to do after a player scores
				}

			}

		}


	}


}//Very End