import socket
import sys
from select import select
import re
import logging

import hashlib
import base64


from threading import Thread
import signal


class BaseHandler(object):
    @property
    def handshake(self):
        return (
                "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
                "Upgrade: WebSocket\r\n"
                "Connection: Upgrade\r\n"
                "Sec-WebSocket-Accept: %(acceptstring)s\r\n"
                "Server: TestTest\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Credentials: true\r\n"
                "\r\n"
                )
    
    
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def handle(self, *args, **kwargs):
        """listen
            handles a single request provoked by the WebSocketServer
            
            :param data: received data.
        """
        raise NotImplementedError("Child need to implemet this!")
    
    # Handshake with this client
    def dohandshake(self, client, server, header, key=None):
        
        logging.debug("Begin handshake: %s" % header)
        
        # Get the handshake template
        handshake = self.handshake
        
        # Step through each header
        for line in header.split('\r\n')[1:]:
            name, value = line.split(': ', 1)
            
            # If this is the key
            if name.lower() == "sec-websocket-key":
                
                # Append the standard GUID and get digest
                combined = value + server.magicGuiId
                response = base64.b64encode(hashlib.sha1(combined).digest())
                
                # Replace the placeholder in the handshake response
                handshake = handshake % { 'acceptstring' : response }
        
        logging.debug("Sending handshake %s" % handshake)
        client.send(handshake)
        return True



# WebSocket server implementation
class WebSocketServer(object):
    
    
    # Constants
    @property
    def magicGuiId(self):
        return "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    @property
    def text(self):
        return 0x01
    @property
    def binary(self):
        return 0x02
    
    @property
    def connections(self):
        return self._connections
    @property
    def listeners(self):
        return self._listeners
    
    
    # Constructor
    def __init__(self, bind, port, cls):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((bind, port))
        self.bind = bind
        self.port = port
        self.cls = cls
        self._connections = {}
        self._listeners = [self.socket]
    
    # Listen for requests
    def listen(self, backlog=5):
        """listen
            Listen to a incomming message from a client. Calls the associated handler of the client to handle the incomming stream.
            
            :param backlog: default 5, specifies the maximum number of queued connections and should be at least 0; the maximum value is system-dependent (usually 5), the minimum value is forced to 0.
        """
        
        self.socket.listen(backlog)
        logging.info("Listening on %s" % self.port)
        
        # Keep serving requests
        self.running = True
        while self.running:
            
            # Find clients that need servicing
            rList, wList, xList = select(self._listeners, [], self._listeners, 1)
            for ready in rList:
                if ready == self.socket:
                    logging.debug("New client connection")
                    client, address = self.socket.accept()
                    fileno = client.fileno()
                    self._listeners.append(fileno)
                    self._connections[fileno] = self.cls(client, self)
                else:
                    logging.debug("Client ready for reading %s" % ready)
                    client = self._connections[ready].client
                    data = client.recv(4096)
                    fileno = client.fileno()
                    if data:
                        self._connections[fileno].handle(data)
                    else:
                        logging.debug("Closing client %s" % ready)
                        #self._connections[fileno].close()
                        del self._connections[fileno]
                        self._listeners.remove(ready)
            
            # Step though and delete broken connections
            for failed in xList:
                if failed == self.socket:
                    logging.error("Socket broke")
                    for fileno, conn in self._connections:
                        conn.close()
                    self.running = False
    
    # broadcast listener
    def broadcast(self, backlog=5, tick=1000, *args, **kwargs):
        """listen
            Listen to a incomming message from a client. Calls the associated handler of the client to handle the incomming stream.
            
            :param backlog: default 5, specifies the maximum number of queued connections and should be at least 0; the maximum value is system-dependent (usually 5), the minimum value is forced to 0.
            :param tick: default 1000, defines the amount of millilsenconds to wait until the message would be send to all clients.
        """
        
        self.socket.listen(backlog)
        logging.info("Broadcast on %s" % self.port)
        
        handler = self.cls(self, tick, *args, **kwargs)
        handler.start()
        
        #server_thread = Thread(target=handler.handle, kwargs={'tick':tick})
        #server_thread.start()
        
        
        # Keep serving broadcast
        self.running = True
        while self.running:
            
            # Find clients that need servicing
            rList, wList, xList = select(self._listeners, [], self._listeners, 1)
            for ready in rList:
                if ready == self.socket:
                    logging.debug("New client connection")
                    client, address = self.socket.accept()
                    fileno = client.fileno()
                    self._listeners.append(fileno)
                    self._connections[fileno] = client
                else:
                    # handle handshake
                    logging.debug("Client ready for reading %s" % ready)
                    client = self._connections[ready]
                    data = client.recv(4096)
                    fileno = client.fileno()
                    if data:
                        header = data
                        if header.find('\r\n\r\n') != -1:
                            parts = header.split('\r\n\r\n', 1)
                            header = parts[0]
                            if handler.dohandshake(client, self, header, parts[1]):
                                logging.info("Handshake successful")
                            else:
                                logging.info("Handshake went wrong")
                    else:
                        logging.debug("Closing client %s" % ready)
                        #self._connections[fileno].close()
                        del self._connections[fileno]
                        self._listeners.remove(ready)


            # Step though and delete broken connections
            for failed in xList:
                if failed == self.socket:
                    logging.error("Socket broke")
                    for fileno, conn in self._connections:
                        conn.close()
                    self.running = False

        # close handler 'cause self (server) stopped
        handler.running = False


