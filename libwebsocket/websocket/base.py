import struct
import socket
import sys
from select import select
import re
import logging

import hashlib
import base64


class BaseHandler(object):
    @property
    def server(self):
        return self._server
    @property
    def client(self):
        return self._client
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
    
    
    def __init__(self, client, server):
        self._client = client
        self._server = server
    
    # Handshake with this client
    def dohandshake(self, header, key=None):
        
        logging.debug("Begin handshake: %s" % header)
        
        # Get the handshake template
        handshake = self.handshake
        
        # Step through each header
        for line in header.split('\r\n')[1:]:
            name, value = line.split(': ', 1)
            
            # If this is the key
            if name.lower() == "sec-websocket-key":
                
                # Append the standard GUID and get digest
                combined = value + self.server.magicGuiId
                response = base64.b64encode(hashlib.sha1(combined).digest())
                
                # Replace the placeholder in the handshake response
                handshake = handshake % { 'acceptstring' : response }
        
        logging.debug("Sending handshake %s" % handshake)
        self.client.send(handshake)
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
    
    
    # Constructor
    def __init__(self, bind, port, cls):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((bind, port))
        self.bind = bind
        self.port = port
        self.cls = cls
        self.connections = {}
        self.listeners = [self.socket]
    
    # Listen for requests
    def listen(self, backlog=5):
        
        self.socket.listen(backlog)
        logging.info("Listening on %s" % self.port)
        
        # Keep serving requests
        self.running = True
        while self.running:
            
            # Find clients that need servicing
            rList, wList, xList = select(self.listeners, [], self.listeners, 1)
            for ready in rList:
                if ready == self.socket:
                    logging.debug("New client connection")
                    client, address = self.socket.accept()
                    fileno = client.fileno()
                    self.listeners.append(fileno)
                    self.connections[fileno] = self.cls(client, self)
                else:
                    logging.debug("Client ready for reading %s" % ready)
                    client = self.connections[ready].client
                    data = client.recv(4096)
                    fileno = client.fileno()
                    if data:
                        self.connections[fileno].feed(data)
                    else:
                        logging.debug("Closing client %s" % ready)
                        #self.connections[fileno].close()
                        del self.connections[fileno]
                        self.listeners.remove(ready)
            
            # Step though and delete broken connections
            for failed in xList:
                if failed == self.socket:
                    logging.error("Socket broke")
                    for fileno, conn in self.connections:
                        conn.close()
                    self.running = False



