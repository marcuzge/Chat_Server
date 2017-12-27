import socket
import sys
import select
import utils

args = sys.argv

class Server(object):
    
    def __init__(self, port):
        self.socket_list = []
        self.socket_name = {}
        self.channel_socks_dict = {} #key: channel, val: sockets
        self.socket_buffer_dict = {} # key: socket, value: data
        self.socket = socket.socket()
        self.socket.bind(("", int(port)))
        self.socket.listen(5)
        self.socket_list.append(self.socket)
    
    def start(self):
        sock_list = []
        while 1:
            # get the list sockets which are ready to be read through select
            # 4th arg, time_out  = 0 : poll and never block
            ready_to_read,ready_to_write,in_error = select.select(self.socket_list,[],[],0)
            for sock in ready_to_read:
                # a new connection request recieved
                if sock == self.socket: 
                    (new_socket, address) = self.socket.accept()
                    self.socket_list.append(new_socket)
                    
                # a message from a client, not a new connection
                else:
                    # process data recieved from client, 
                    try:
                        # receiving data from the socket.
                        data = sock.recv(utils.MESSAGE_LENGTH)
                        if data:
                            data = self.buffer(sock, data)
                            # print(data)
                            if not data:
                                continue
                            # data = data.rstrip();
                            # there is something in the socket
                            #     broadcast(self.socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data) 

                            # print data
                            # print sock

                            if sock not in self.socket_name.keys():
                                self.socket_name[sock] = data.rstrip()
                            else:
                                # retrive channels
                                for channel in self.channel_socks_dict.keys():
                                    for socket in self.channel_socks_dict[channel]:
                                        if sock == socket:
                                            sock_list = self.channel_socks_dict[channel]
                                # print name
                                # control msg
                                if data[0] == "/":
                                    self.switch(data, sock, self.socket_name[sock])
                                # normal msg
                                else:
                                    if len(sock_list) == 0:
                                        sock.send(utils.SERVER_CLIENT_NOT_IN_CHANNEL.ljust(utils.MESSAGE_LENGTH))
                                    # print (sock_list)
                                    self.broadcast(sock, sock_list, '[' + self.socket_name[sock] + '] ' + data.rstrip())
                        else:                                   
                            if sock in self.socket_name:
                                self.socket_name.remove(sock)

                            # at this stage, no data means probably the connection has been broken
                            self.broadcast(sock, sock_list, utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.socket_name[sock])) 
                            

                    #exception 
                    except:
                        self.remove_socket(sock)
                        continue

        self.socket.close() 

    # broadcast chat messages to all connected clients
    def broadcast (self, sock, sock_list, message):
        for socket in sock_list:
            # send the message only to peer
            if socket is not self.socket and socket is not sock :

                try :
                    socket.send(message.ljust(utils.MESSAGE_LENGTH))
                except :
                    # broken socket connection
                    socket.close()
                    # broken socket, remove it
                    if socket in self.socket_list:
                        self.socket_list.remove(socket)

    def already_in_channel(self, sock):
        for channel in self.channel_socks_dict.keys():
                for socket in self.channel_socks_dict[channel]:
                    if sock == socket:
                        return True
        return False

    def remove_socket(self, sock):
        for channel in self.channel_socks_dict.keys():
            for socket in self.channel_socks_dict[channel]:
                if sock == socket:
                    # print "bla bla bla"
                    self.channel_socks_dict[channel].remove(socket)
                    if self.channel_socks_dict[channel]:
                        # print "za za za"
                        self.broadcast(sock, self.channel_socks_dict[channel], utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.socket_name[sock]))

    
    def switch(self, data, sock, name):
        if data.split(' ', 1)[0] == '/join':
            if len(data.split(' ', 1)) != 2 or data.split(' ', 1)[1].strip() == "":
                sock.send(utils.SERVER_JOIN_REQUIRES_ARGUMENT.ljust(utils.MESSAGE_LENGTH))
            else:
                self.join(data.split(' ', 1)[1].rstrip(), sock, name)
        elif data.split(' ', 1)[0] == '/create':
            if len(data.split(' ', 1)) != 2 or data.split(' ', 1)[1].strip() == "":
                sock.send(utils.SERVER_CREATE_REQUIRES_ARGUMENT.ljust(utils.MESSAGE_LENGTH))
            else:
                self.create(data.split(' ', 1)[1].rstrip(), sock)
        elif data.split(' ', 1)[0] == '/list':
            self.list(sock)
        else:
            # print(data+" invalid")
            sock.send(utils.SERVER_INVALID_CONTROL_MESSAGE.format(data.split(' ', 1)[0]).ljust(utils.MESSAGE_LENGTH))
    

    def join(self, channelName, sock, name):
        if channelName in self.channel_socks_dict.keys():
            if (self.already_in_channel(sock)):
                self.remove_socket(sock)
            self.channel_socks_dict[channelName].append(sock)
            self.broadcast(sock, self.channel_socks_dict[channelName], utils.SERVER_CLIENT_JOINED_CHANNEL.format(name))
        else:
            sock.send(utils.SERVER_NO_CHANNEL_EXISTS.format(channelName).ljust(utils.MESSAGE_LENGTH)) 
    

    def create(self, channel, sock):
        if channel in self.channel_socks_dict.keys():
            sock.send(utils.SERVER_CHANNEL_EXISTS.format(channel).ljust(utils.MESSAGE_LENGTH))
        else:
            if (self.already_in_channel(sock)):
                self.remove_socket(sock)
            self.channel_socks_dict[channel] = [sock]
    

    def list(self, sock):
        for channel in self.channel_socks_dict.keys():
            sock.send(channel.ljust(utils.MESSAGE_LENGTH))

    def buffer(self, sock, data):
        buffered_data = ""
        all_data = ""
        if sock not in self.socket_buffer_dict.keys():
            if len(data) == utils.MESSAGE_LENGTH:
                return data
            else:
                socket_buffer_dict[sock] = data
        else:
            all_data = self.socket_buffer_dict[sock] + data
            if len(all_data) >= utils.MESSAGE_LENGTH:                    
                buffered_data = all_data[:utils.MESSAGE_LENGTH]
                self.socket_buffer_dict[sock] = all_data[utils.MESSAGE_LENGTH:]
                return buffered_data
            else:
                self.socket_buffer_dict[sock] = all_data
               

if len(args) != 2:
    print ("Please supply a port.")
    sys.exit()
server = Server(args[1])
server.start()
