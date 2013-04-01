import logging, os
from time import sleep

from libwebsocket.websocket.broadcast import BroadcastHandler


import xml.etree.cElementTree as ET
import json


class CryEngineHandler(BroadcastHandler):
    
    @property
    def file(self):
        return self._file
    
    def __init__(self, server, tick, file, *args, **kwargs):
        super(CryEngineHandler, self).__init__(server, tick, *args, **kwargs)
        self._file = file
    
    
    def tick(self, *args, **kwargs):
        ''' '''
        out = []
        
        for event, elem in ET.iterparse(os.path.abspath(self.file)):
            if elem.tag == "Node":
                pos = elem.attrib["Position_xyz"].split(",")
                out.append({
                           'x' : pos[0],
                           'y' : pos[1],
                           'z' : pos[2],
                           'yaw' : elem.attrib["Yaw"]
                })
        
        for id in self.server.connections:
            logging.info("sending message to %s" % str(id))
            self.sendMessage(self.server.connections[id], json.dumps(out))
    