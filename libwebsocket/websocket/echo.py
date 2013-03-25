import logging

from base import BaseHandler


# WebSocket implementation
class EchoHandler(BaseHandler):
    
    # Constructor
    def __init__(self, client, server):
        super(EchoHandler, self).__init__(client, server)
        
        self.handshaken = False
        self.header = ""
        self.data = ""
    
    
    # Serve this client
    def feed(self, data):
        
        # If we haven't handshaken yet
        if not self.handshaken:
            logging.debug("No handshake yet")
            self.header += data
            if self.header.find('\r\n\r\n') != -1:
                parts = self.header.split('\r\n\r\n', 1)
                self.header = parts[0]
                if self.dohandshake(self.header, parts[1]):
                    logging.info("Handshake successful")
                    self.handshaken = True
        
        # We have handshaken
        else:
            logging.debug("Handshake is complete")
            
            # Decode the data that we received according to section 5 of RFC6455
            recv = self.decodeCharArray(data)
            
            # Send our reply
            self.sendMessage(''.join(recv).strip());
    
    
    # Stolen from http://www.cs.rpi.edu/~goldsd/docs/spring2012-csci4220/websocket-py.txt
    def sendMessage(self, s):
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
        self.client.send(str(message))
    
    
    # Stolen from http://stackoverflow.com/questions/8125507/how-can-i-send-and-receive-websocket-messages-on-the-server-side
    def decodeCharArray(self, stringStreamIn):
        
        # Turn string values into opererable numeric byte values
        byteArray = [ord(character) for character in stringStreamIn]
        datalength = byteArray[1] & 127
        indexFirstMask = 2
        
        if datalength == 126:
            indexFirstMask = 4
        elif datalength == 127:
            indexFirstMask = 10
        
        # Extract masks
        masks = [m for m in byteArray[indexFirstMask : indexFirstMask+4]]
        indexFirstDataByte = indexFirstMask + 4
        
        # List of decoded characters
        decodedChars = []
        i = indexFirstDataByte
        j = 0
        
        # Loop through each byte that was received
        while i < len(byteArray):
            
            # Unmask this byte and add to the decoded buffer
            decodedChars.append( chr(byteArray[i] ^ masks[j % 4]) )
            i += 1
            j += 1
        
        # Return the decoded string
        return decodedChars
    
    
#def onmessage(self, data):
#logging.info("Got message: %s" % data)
#self.send(data)

#def send(self, data):
#logging.info("Sent message: %s" % data)
#self.client.send("\x00%s\xff" % data)

#def close(self):
#self.client.close()

