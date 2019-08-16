import threading
import pygame
import random
import enum
import socket
import select

# Window size
WINDOW_WIDTH=400
WINDOW_HEIGHT=400

DARK    = (  50, 50, 50 )
WHITE   = ( 255,255,255 )
RED     = ( 255, 55, 55 )
GREEN   = (   5,255, 55 )
BLUE    = (   5, 55,255 )

LISTEN_ADDRESS = '127.0.0.1'
LISTEN_PORT    = 5555


class NetworkEvents( enum.IntEnum ):
    CLIENT_CONNECTED = pygame.USEREVENT + 1
    CLIENT_HANGUP    = pygame.USEREVENT + 2
    CLIENT_MESSAGE   = pygame.USEREVENT + 3


class AlienSprite( pygame.sprite.Sprite ):
    """ A tiny little alien, which wanders around the screen """
    def __init__( self, colour ):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.render( colour )
        self.rect  = self.image.get_rect()
        self.rect.center = ( random.randrange( 0, WINDOW_WIDTH ), random.randrange( 0, WINDOW_HEIGHT ) )

    def render( self, colour ):
        new_image = pygame.Surface( ( 7, 6 ), pygame.SRCALPHA )
        new_image.fill( (0,0,0,0) )
        pixels = [                     (3,1),               \
                                (2,2), (3,2), (4,2),        \
                            (1,3),     (3,3),      (5,3),   \
                                (2,4), (3,4), (4,4) ]
        for p in pixels:
            new_image.set_at( p, colour )
        return new_image

    def update( self ):
        self.rect.x += random.randrange( -2, 3 )
        self.rect.y += random.randrange( -2, 3 )
        # remove if we wander off-screen
        if ( self.rect.x < 0 or self.rect.x >= WINDOW_WIDTH or \
             self.rect.y < 0 or self.rect.x >= WINDOW_HEIGHT ):
            self.kill() 




class ConversationHandlerThread( threading.Thread ):
    """ A thread that handles a conversation with a single remote client.
        Accepts commands of 'red', 'green' or 'blue', and posts messages
        to the main PyGame thread for processing """
    def __init__( self, client_socket, client_address ):
        threading.Thread.__init__(self)
        self.client_socket  = client_socket
        self.client_address = client_address
        self.data_buffer    = ''
        self.daemon         = True # exit with parent
        self.done           = False

    def stop( self ):
        self.done = True

    def run( self ):
        """ Loops until the client hangs-up """
        read_events_on   = [ self.client_socket ]
        while ( not self.done ):
            # Wait for incoming data, or errors, or 0.3 seconds
            (read_list, write_list, except_list) = select.select( read_events_on, [], [], 0.5 )

            if ( len( read_list ) > 0 ):
                # New data arrived, read it
                incoming = self.client_socket.recv( 8192 )
                if ( len(incoming) == 0):
                    # Socket has closed
                    new_event = pygame.event.Event( NetworkEvents.CLIENT_HANGUP, { "address" : self.client_address } )
                    pygame.event.post( new_event )
                    self.client_socket.close()
                    self.done = True
                else:
                    # Data has arrived
                    try:
                        new_str = incoming.decode('utf-8')
                        self.data_buffer += new_str
                    except: 
                        pass # don't understand buffer

                    # Parse incoming message (trivial parser, not high quality) 
                    # commands are '\n' separated
                    if (self.data_buffer.find('\n') != -1 ):
                        for line in self.data_buffer.split('\n'):
                            line = line.strip()
                            # client disconnect command
                            if ( line == 'close' ):
                                new_event = pygame.event.Event( NetworkEvents.CLIENT_HANGUP, { "address" : self.client_address } )
                                pygame.event.post( new_event )
                                self.client_socket.close()
                                self.done = True

                            # only make events for valid commands
                            elif ( line in ( 'red', 'green', 'blue' ) ):
                                new_event = pygame.event.Event( NetworkEvents.CLIENT_MESSAGE, { "address" : self.client_address, "message" : line  } )
                                pygame.event.post( new_event )
                        self.data_buffer = ''  # all used-up






class ConnectionHandlerThread( threading.Thread ):
    """ Opens a socket, listening for incoming connections.
        If a client connects, notifies the PyGame main thread with a message,
        and starts a conversation handler thread to accept commands """
    def __init__( self ):
        threading.Thread.__init__(self)
        self.daemon = True # exit with parent
        self.done   = False

    def stop( self ):
        self.done = True

    def run( self ):
        # Establish a socket-listener
        rx_sock = socket.socket() 
        rx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        rx_sock.bind( ( LISTEN_ADDRESS, LISTEN_PORT ) )
        while ( not self.done ):
            rx_sock.listen( 3 ) # small queue
            client_socket, remote_addr = rx_sock.accept()
            print("Connection from %s" % ( str( remote_addr ) ) )
            # Tell the main thread someone connected via an event
            new_event_args = { "socket"  : client_socket, "address" : remote_addr  }
            new_event = pygame.event.Event( NetworkEvents.CLIENT_CONNECTED, new_event_args )
            pygame.event.post( new_event )
            # Start a thread to handle the socket-conversation with the client
            new_thread = ConversationHandlerThread( client_socket, remote_addr )
            new_thread.start()




###
### MAIN
###

# Create the window
pygame.init()
pygame.display.set_caption("Socket Messages")
WINDOW  = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE )

# Create some sprites
SPRITES = pygame.sprite.Group()
for i in range( 3 ):
    new_sprite = AlienSprite( WHITE )
    SPRITES.add( new_sprite )

# Start the connection-listener thread
thread1 = ConnectionHandlerThread()
thread1.start()

# Main paint / update / event loop
done = False
clock = pygame.time.Clock()
while ( not done ):
    SPRITES.update()

    for event in pygame.event.get():
        if ( event.type == pygame.QUIT ):
            done = True

        elif ( event.type == NetworkEvents.CLIENT_HANGUP ):
            print(" CLIENT DISCONNECTED %s " % ( str(event.address) ) )

        elif ( event.type == NetworkEvents.CLIENT_CONNECTED ):
            print(" NEW CLIENT FROM %s " % ( str(event.address) ) )

        elif ( event.type == NetworkEvents.CLIENT_MESSAGE ):
            print(" CLIENT MESSAGE FROM %s - %s " % ( str(event.address), event.message ) )
            if ( event.message == 'red' ):
                new_sprite = AlienSprite( RED )
                SPRITES.add( new_sprite )
            elif ( event.message == 'blue' ):
                new_sprite = AlienSprite( BLUE )
                SPRITES.add( new_sprite )
            elif ( event.message == 'green' ):
                new_sprite = AlienSprite( GREEN )
                SPRITES.add( new_sprite )

        elif ( event.type == pygame.VIDEORESIZE ):
            WINDOW_WIDTH  = event.w
            WINDOW_HEIGHT = event.h
            WINDOW  = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE )

    WINDOW.fill( DARK )
    SPRITES.draw( WINDOW )
    pygame.display.flip()

    clock.tick_busy_loop(60)

thread1.stop()
pygame.quit()