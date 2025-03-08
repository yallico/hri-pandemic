init python:
    import socket
    import json
    import threading
    import time
    
    # NAO Communication Manager
    class NAOComms:
        def __init__(self, host='localhost', port=9999):
            """Initialize the NAO communication manager"""
            self.host = host
            self.port = port
            self.socket = None
            self.connected = False
            self.lock = threading.RLock()
            renpy.log("NAO Communication Manager initialized")
        
        def connect(self):
            """Connect to the NAO socket server"""
            with self.lock:
                if self.connected:
                    return True
                
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect((self.host, self.port))
                    self.connected = True
                    renpy.log(f"Connected to NAO server at {self.host}:{self.port}")
                    return True
                except Exception as e:
                    renpy.log(f"Failed to connect to NAO server: {e}")
                    self.socket = None
                    self.connected = False
                    return False
        
        def disconnect(self):
            """Disconnect from the NAO socket server"""
            with self.lock:
                if not self.connected:
                    return
                
                try:
                    self.socket.close()
                except:
                    pass
                
                self.socket = None
                self.connected = False
                renpy.log("Disconnected from NAO server")
        
        def send_message(self, turn, text):
            """Send a message to the NAO socket server"""
            with self.lock:
                if not self.connected and not self.connect():
                    renpy.log("Cannot send message: Not connected to NAO server")
                    return False
                
                try:
                    # Create message
                    message = {
                        "turn": turn,
                        "text": text
                    }
                    
                    # Send message
                    message_str = json.dumps(message)
                    self.socket.send(message_str.encode('utf-8'))
                    renpy.log(f"Sent message to NAO server: {message_str}")
                    
                    # Wait for acknowledgment (with timeout)
                    self.socket.settimeout(5.0)
                    response = self.socket.recv(4096).decode('utf-8')
                    renpy.log(f"Received response from NAO server: {response}")
                    
                    return True
                
                except Exception as e:
                    renpy.log(f"Error sending message to NAO server: {e}")
                    self.disconnect()
                    return False

    # Create a global instance of the NAO communication manager
    nao_comms = NAOComms()

    # Function to send a message to NAO after a turn
    def send_to_nao(message, turn_number=None):
        """Send a message to NAO and handle connection issues"""
        if turn_number is None:
            turn_number = turn
        
        # Try to send the message
        success = nao_comms.send_message(turn_number, message)
        
        # Log the result
        if success:
            renpy.log(f"Successfully sent message to NAO for turn {turn_number}")
        else:
            renpy.log(f"Failed to send message to NAO for turn {turn_number}")
        
        return success

# Label to disconnect from NAO server when the game ends
label nao_disconnect:
    python:
        # Disconnect from NAO server
        nao_comms.disconnect()
    return 