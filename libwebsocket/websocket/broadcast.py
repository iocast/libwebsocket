import struct

import logging
from threading import Thread

from time import sleep

from base import BaseHandler

# WebSocket implementation
class BroadcastHandler(BaseHandler, Thread):
    
    @property
    def server(self):
        return self._server
    @property
    def tick_time(self):
        return self._tick_time

    def __init__(self, server, tick, *args, **kwargs):
        super(BroadcastHandler, self).__init__(*args, **kwargs)
        self._server = server
        self._tick_time = tick
        
    def run(self):
        """handle
        >>> help(BaseHandler.handle)
        """

        logging.info("Broadcast every %s" % str(self.tick))

        # Keep serving broadcast
        self.running = True
        while self.running:
            
            if len(self.server.connections) > 0:
                self.tick()

            sleep(self.tick_time/1000.0)


    def tick(self):
        raise NotImplementedError("Child need to implemet this!")



    def sendMessage(self, client, s):
        """
            Encode and send a WebSocket message
            """
        
        # Empty message to start with
        message = ""
        
        # always send an entire message as one frame (fin)
        b1 = 0x80
        
        # in Python 2, strs are bytes and unicodes are strings
        if type(s) == unicode:
            b1 |= self.server.text
            payload = s.encode("UTF8")
        
        elif type(s) == str:
            b1 |= self.server.text
            payload = s
        
        # Append 'FIN' flag to the message
        message += chr(b1)
        
        # never mask frames from the server to the client
        b2 = 0
        
        # How long is our payload?
        length = len(payload)
        if length < 126:
            b2 |= length
            message += chr(b2)
        
        elif length < (2 ** 16) - 1:
            b2 |= 126
            message += chr(b2)
            l = struct.pack(">H", length)
            message += l
        
        else:
            l = struct.pack(">Q", length)
            b2 |= 127
            message += chr(b2)
            message += l
        
        # Append payload to message
        message += payload
        
        # Send to the client
        client.send(str(message))


    
