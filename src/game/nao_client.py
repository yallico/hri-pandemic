#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json
import time
import logging
import sys

# Import NAO SDK (assuming Python 2.7 on NAO)
try:
    from naoqi import ALProxy
    NAO_SDK_AVAILABLE = True
except ImportError:
    print("NAOqi Python SDK not found. Running in simulation mode.")
    NAO_SDK_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nao_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NAO_Client")

class NAOClient:
    def __init__(self, server_ip='localhost', server_port=9998, nao_ip='localhost', nao_port=9559):
        """
        Initialize the NAO client
        
        Args:
            server_ip (str): IP address of the socket server
            server_port (int): Port of the socket server
            nao_ip (str): IP address of the NAO robot (localhost if this script runs on NAO)
            nao_port (int): Port of the NAO robot's NaoQi (default: 9559)
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.nao_ip = nao_ip
        self.nao_port = nao_port
        
        # Socket for server communication
        self.socket = None
        
        # NAO text-to-speech proxy
        self.tts = None
        
        # Track if client is running
        self.running = False
        
        logger.info("NAO Client initialized")
        
        # Initialize NAO connection if SDK available
        if NAO_SDK_AVAILABLE:
            try:
                self.tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)
                logger.info("Connected to NAO TTS service")
            except Exception as e:
                logger.error(f"Failed to connect to NAO: {e}")
                self.tts = None
    
    def connect_to_server(self):
        """Connect to the socket server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            logger.info(f"Connected to server at {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            return False
    
    def start(self):
        """Start the client and listen for messages from the server"""
        if not self.connect_to_server():
            logger.error("Could not connect to server. Exiting.")
            return
        
        self.running = True
        logger.info("NAO Client started")
        
        try:
            while self.running:
                try:
                    # Receive data from server
                    data = self.socket.recv(4096)
                    if not data:
                        logger.warning("Server closed connection")
                        break
                    
                    # Parse the message from the server
                    message = data.decode('utf-8')
                    logger.info(f"Received from server: {message}")
                    
                    # Process the message
                    self._process_message(message)
                    
                except socket.timeout:
                    # Socket timeout, continue
                    continue
                except Exception as e:
                    logger.error(f"Error receiving data: {e}")
                    # Try to reconnect
                    if not self.connect_to_server():
                        logger.error("Failed to reconnect. Exiting.")
                        break
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()
    
    def _process_message(self, message):
        """Process messages received from the server"""
        try:
            # Parse the message as JSON
            data = json.loads(message)
            
            if "action" in data:
                action = data["action"]
                
                # Handle the "say" action
                if action == "say" and "text" in data:
                    text = data["text"]
                    turn = data.get("turn", "unknown")
                    logger.info(f"Saying text for turn {turn}: {text}")
                    
                    # Say the text on NAO
                    self._say_text(text)
                    
                    # Send acknowledgment back to the server
                    response = json.dumps({"status": "ok", "action": action, "turn": turn})
                    self.socket.send(response.encode('utf-8'))
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _say_text(self, text):
        """Make NAO say the text"""
        if self.tts:
            try:
                self.tts.say(text)
                logger.info(f"NAO said: {text}")
            except Exception as e:
                logger.error(f"Error making NAO speak: {e}")
        else:
            # Simulation mode, just print the text
            logger.info(f"[SIMULATION] NAO would say: {text}")
            print(f"NAO says: {text}")
    
    def stop(self):
        """Stop the client and close the connection"""
        self.running = False
        
        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        logger.info("NAO Client stopped")


if __name__ == "__main__":
    # Get command-line arguments for server IP and port
    server_ip = 'localhost'
    server_port = 9998
    nao_ip = 'localhost'
    nao_port = 9559
    
    # Override defaults with command-line arguments if provided
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    if len(sys.argv) > 2:
        server_port = int(sys.argv[2])
    if len(sys.argv) > 3:
        nao_ip = sys.argv[3]
    if len(sys.argv) > 4:
        nao_port = int(sys.argv[4])
    
    # Create and start the client
    client = NAOClient(server_ip, server_port, nao_ip, nao_port)
    client.start() 