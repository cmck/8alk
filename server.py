import socket, select, sys, pickle, atexit
from collections import deque

#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)

# Send data to client
def send_data(sock, message):
    for socket in CONNECTION_LIST:
        if socket == sock:
            try:
                socket.send(message)
            except :
                socket.close()
                CONNECTION_LIST.remove(socket) 

# Persist chat object
def persist_chat():
    print 'Saving chat history to file'
    try:
        pickle.dump(hist, open('hist.p', 'w'))
    except IOError:
        pass

if __name__ == "__main__":
    if(len(sys.argv) < 2) :
        print 'Usage : python server.py  port'
        sys.exit()
     
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    PEERNAME_DICT = {}
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = int(sys.argv[1])
   
    # Init chat history
    hist = []
    try:
        hist = pickle.load(open('hist.p', 'r'))
    except EOFError, IOError:
	    pass
    hist = deque(hist, 100)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)

    # Handle script exit
    atexit.register(persist_chat)
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)

                # Set the default peername for this client
                PEERNAME_DICT[sockfd] = str(sockfd.getpeername())

                print "Client (%s, %s) connected" % addr
                broadcast_data(sockfd, "\n[%s:%s] entered room\n" % addr)
                send_data(sockfd, ''.join(hist))

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)

                    # data is new nickname
                    if data.startswith('/nick'):
                        new_nick = str(data.split(' ')[1]).rstrip()
                        old_nick = PEERNAME_DICT[sock]
                        PEERNAME_DICT[sock] = new_nick
                        print "Client (%s, %s) nick changed" % addr
                        msg = "\nClient %s changed nickname to %s\n" % (old_nick, new_nick)
                        broadcast_data(sock, msg)

                    # data is a chat message
                    else:
                        msg = "\r" + '<' + PEERNAME_DICT[sock] + '> ' + data
                        hist.append(msg)
                        broadcast_data(sock, msg)                
                 
                except:
                    broadcast_data(sock, "Client (%s, %s) is offline\n" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    del PEERNAME_DICT[sock]
                    continue
     
    server_socket.close()