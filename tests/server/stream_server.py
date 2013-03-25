import logging
import sys, os

from threading import Thread
import signal
import time



sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../")

from libwebsocket.websocket.base import WebSocketServer
from libwebsocket.websocket.stream import StreamHandler


# Entry point
if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    server = WebSocketServer("localhost", 8080, StreamHandler)
    server_thread = Thread(target=server.listen, args=[5])
    server_thread.start()
    
    # Add SIGINT handler for killing the threads
    def signal_handler(signal, frame):
        logging.info("Caught Ctrl+C, shutting down...")
        server.running = False
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        time.sleep(100)


