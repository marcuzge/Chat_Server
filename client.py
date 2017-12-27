import socket
import sys
import select
import utils

class Client(object):

    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = int(port)
        self.socket = socket.socket()
        self.alldata = ""

        try:
            self.socket.connect((self.address, self.port))
        except:
            sys.stdout.write(utils.CLIENT_CANNOT_CONNECT.format(self.address, self.port)+ '\n')
            sys.exit()


        self.socket.send(name.ljust(utils.MESSAGE_LENGTH))
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush() 

        while 1:
            socket_list = [sys.stdin, self.socket]

            # Get the list sockets which are readable
            ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])

            for sock in ready_to_read:             
                if sock == self.socket:
                    data = sock.recv(utils.MESSAGE_LENGTH)    
                    if data:
                        self.alldata += data
                        if len(self.alldata) >= utils.MESSAGE_LENGTH :
                            output = self.alldata[: utils.MESSAGE_LENGTH].rstrip()
                            sys.stdout.write(utils.CLIENT_WIPE_ME + "\r")
                            sys.stdout.write(output + "\n")
                            sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()
                            self.alldata = self.alldata[utils.MESSAGE_LENGTH:]
                else:
                    msg = sys.stdin.readline().rstrip('\n')
                    # print(msg)
                    if len(msg) < utils.MESSAGE_LENGTH:
                        msg = msg.ljust(utils.MESSAGE_LENGTH)                    
                    self.socket.send(msg)
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()




args = sys.argv
if len(args) != 4:
    print ("Please supply a server address and port.")
    sys.exit()
client = Client(args[1], args[2], args[3])
