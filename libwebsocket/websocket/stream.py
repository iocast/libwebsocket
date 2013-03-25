import logging

from base import BaseHandler


# WebSocket implementation
class StreamHandler(BaseHandler):

    def __init__(self, client, server):
        super(StreamHandler, self).__init__(client, server)
        
        self.header = ""
        self.data = ""