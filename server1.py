import socket


host = "127.0.0.1"
port = 5278
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()
print("Socket now listening")
while True:
    conn, addr = s.accept()
    print ("Connected with" + addr[0] + ':' + str(addr[1]))
    # pygame.surfarray.array2d(screen)
    # data = screen
    data = conn.recv(1024)
    print(data.decode())
    conn.send("server received you message.".encode())
conn.close()
s.close()

# import socket
# import sys
# from thread import *
# HOST = ''  # Symbolic name meaning all available interfaces
# PORT = 8888 # Arbitrary non-privileged port
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print 'Socket created'
# #Bind socket to local host and port
# try:
# s.bind((HOST, PORT))
# except socket.error , msg:
# print 'Bind failed. Error Code : '   str(msg[0])   ' Message '   msg[1]
# sys.exit()
# print 'Socket bind complete'
# #Start listening on socket
# s.listen(10)
# print 'Socket now listening'
# #Function for handling connections. This will be used to create threads
# def clientthread(conn):
# #Sending message to connected client
# conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string
# #infinite loop so that function do not terminate and thread do not end.
# while True:
# #Receiving from client
# data = conn.recv(1024)
# reply = 'OK...'   data
# if not data: 
# break
# conn.sendall(reply)
# #came out of loop
# conn.close()
# #now keep talking with the client
# while 1:
# #wait to accept a connection - blocking call
# conn, addr = s.accept()
# print 'Connected with '   addr[0]   ':'   str(addr[1])
# #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
# start_new_thread(clientthread ,(conn,))
# s.close()