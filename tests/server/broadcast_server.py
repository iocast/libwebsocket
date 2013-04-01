import logging
import sys, os

from threading import Thread
import signal
import time



sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../")

from libwebsocket.websocket.base import WebSocketServer
from handler.cry_engine import CryEngineHandler


# Entry point
if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    server = WebSocketServer("localhost", 8080, CryEngineHandler)
    server_thread = Thread(target=server.broadcast, args=[5], kwargs={'tick':20000, 'file':'../data/Position_Node.xml'})
    server_thread.start()
    
    # Add SIGINT handler for killing the threads
    def signal_handler(signal, frame):
        logging.info("Caught Ctrl+C, shutting down...")
        server.running = False
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        time.sleep(100)


