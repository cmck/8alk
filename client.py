import socket, select, string, sys
 
def prompt() :
    nick_display = "<%s> " % nick
    sys.stdout.write(nick_display)
    sys.stdout.flush()
 
#main function
if __name__ == "__main__":
     
    if(len(sys.argv) < 4) :
        print 'Usage : python telnet.py hostname port nickname'
        sys.exit()
     
    host = sys.argv[1]
    port = int(sys.argv[2])
    nick = sys.argv[3]
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
    
    # set the nickname
    s.send("/nick " + nick)

    print 'Connected to remote host. Start sending messages'
    prompt()

    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    sys.stdout.write('\a')
                    sys.stdout.flush()
                    sys.stdout.write(data)
                    prompt()
             
            #user entered a message
            else :
                msg = sys.stdin.readline()
                if msg.startswith('/nick'):
                    nick = str(msg.split(' ')[1]).rstrip()
                s.send(msg)
                prompt()
