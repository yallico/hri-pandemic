#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
import time
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nao_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NAO_Server")

class NAOServer:
    def __init__(self, host='0.0.0.0', game_port=9999, nao_port=9998):
        """
        Initialize the NAO socket server with two sockets:
        1. Game socket: Receives events from the Ren'Py game
        2. NAO socket: Sends commands to the NAO robot
        
        Args:
            host (str): Host address to bind to
            game_port (int): Port for game communication
            nao_port (int): Port for NAO communication
        """
        self.host = host
        self.game_port = game_port
        self.nao_port = nao_port
        
        # Socket for Ren'Py game communication
        self.game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Socket for NAO communication
        self.nao_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nao_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Client connections
        self.game_conn = None
        self.nao_conn = None
        
        # Track if server is running
        self.running = False
        
        # Store messages that should be sent to NAO
        self.messages_to_nao = []
        
        logger.info("NAO Server initialized")
    
    def start(self):
        """Start the server with separate threads for game and NAO connections"""
        self.running = True
        
        # Start game server
        game_thread = threading.Thread(target=self._run_game_server)
        game_thread.daemon = True
        game_thread.start()
        
        # Start NAO server
        nao_thread = threading.Thread(target=self._run_nao_server)
        nao_thread.daemon = True
        nao_thread.start()
        
        logger.info("NAO Server started")
        
        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def _run_game_server(self):
        """Run the socket server that listens for game events"""
        try:
            self.game_socket.bind((self.host, self.game_port))
            self.game_socket.listen(1)
            logger.info(f"Game server listening on {self.host}:{self.game_port}")
            
            while self.running:
                # Accept connections from the game
                self.game_conn, addr = self.game_socket.accept()
                logger.info(f"Game connected from {addr}")
                
                # Handle game messages
                while self.running:
                    try:
                        # Receive data from game
                        data = self.game_conn.recv(4096)
                        if not data:
                            break
                        
                        # Parse the message from the game
                        message = data.decode('utf-8')
                        logger.info(f"Received from game: {message}")
                        
                        # Process the message
                        self._process_game_message(message)
                        
                    except Exception as e:
                        logger.error(f"Error handling game message: {e}")
                        break
                
                # Close connection if loop exited
                if self.game_conn:
                    self.game_conn.close()
                    self.game_conn = None
        
        except Exception as e:
            logger.error(f"Game server error: {e}")
        finally:
            if self.game_socket:
                self.game_socket.close()
    
    def _run_nao_server(self):
        """Run the socket server that sends commands to the NAO robot"""
        try:
            self.nao_socket.bind((self.host, self.nao_port))
            self.nao_socket.listen(1)
            logger.info(f"NAO server listening on {self.host}:{self.nao_port}")
            
            while self.running:
                # Accept connections from NAO
                self.nao_conn, addr = self.nao_socket.accept()
                logger.info(f"NAO connected from {addr}")
                
                # Send pending messages to NAO
                self._send_pending_messages()
                
                # Handle NAO communication
                while self.running:
                    try:
                        # Check if there are messages to send
                        if self.messages_to_nao and self.nao_conn:
                            message = self.messages_to_nao.pop(0)
                            self._send_to_nao(message)
                        
                        # Minimal delay to prevent CPU overuse
                        time.sleep(0.1)
                        
                        # Check if NAO is still connected
                        self.nao_conn.settimeout(0.0)  # Non-blocking
                        test_data = self.nao_conn.recv(1)
                        if not test_data:  # Connection closed
                            logger.info("NAO disconnected")
                            break
                    
                    except socket.timeout:
                        # No data available, continue
                        pass
                    except BlockingIOError:
                        # Non-blocking socket, continue
                        pass
                    except Exception as e:
                        logger.error(f"Error in NAO communication: {e}")
                        break
                
                # Close connection if loop exited
                if self.nao_conn:
                    self.nao_conn.close()
                    self.nao_conn = None
        
        except Exception as e:
            logger.error(f"NAO server error: {e}")
        finally:
            if self.nao_socket:
                self.nao_socket.close()
    
    def _process_game_message(self, message):
        """Process messages received from the game"""
        try:
            # Parse the message as JSON
            data = json.loads(message)
            
            if "turn" in data and "text" in data:
                turn = data["turn"]
                text = data["text"]
                logger.info(f"Processing message for turn {turn}: {text}")
                
                # Add message to queue to be sent to NAO
                self.messages_to_nao.append({
                    "action": "say",
                    "text": text,
                    "turn": turn
                })
                
                # Try to send immediately if NAO is connected
                if self.nao_conn:
                    self._send_pending_messages()
                
                # Send acknowledgment back to the game
                if self.game_conn:
                    response = json.dumps({"status": "ok", "received": data})
                    self.game_conn.send(response.encode('utf-8'))
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error processing game message: {e}")
    
    def _send_pending_messages(self):
        """Send any pending messages to NAO"""
        if not self.nao_conn or not self.messages_to_nao:
            return
        
        # Send all pending messages
        while self.messages_to_nao:
            message = self.messages_to_nao.pop(0)
            self._send_to_nao(message)
    
    def _send_to_nao(self, message):
        """Send a message to the NAO robot"""
        if not self.nao_conn:
            logger.warning("Cannot send to NAO: Not connected")
            # Put the message back in the queue
            self.messages_to_nao.insert(0, message)
            return
        
        try:
            # Convert message to JSON string
            message_str = json.dumps(message)
            self.nao_conn.send(message_str.encode('utf-8'))
            logger.info(f"Sent to NAO: {message_str}")
            
            # Wait for acknowledgment from NAO
            self.nao_conn.settimeout(5.0)  # 5 second timeout
            response = self.nao_conn.recv(1024).decode('utf-8')
            logger.info(f"NAO response: {response}")
            
        except Exception as e:
            logger.error(f"Error sending to NAO: {e}")
            # If failed to send, put the message back in the queue
            self.messages_to_nao.insert(0, message)
            
            # Close the connection as it might be broken
            self.nao_conn.close()
            self.nao_conn = None
    
    def stop(self):
        """Stop the server and close all connections"""
        self.running = False
        
        # Close connections
        if self.game_conn:
            self.game_conn.close()
        if self.nao_conn:
            self.nao_conn.close()
        
        # Close sockets
        if self.game_socket:
            self.game_socket.close()
        if self.nao_socket:
            self.nao_socket.close()
        
        logger.info("NAO Server stopped")


if __name__ == "__main__":
    # Create and start the server
    server = NAOServer()
    server.start() 