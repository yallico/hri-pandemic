"""
Robot Control Module for NAO/Pepper integration with Renpy
This module enables communication between the Renpy game and a NAO/Pepper robot via socket connection.
"""

import socket
import threading
import time
import os

class RobotServer:
    def __init__(self, host='0.0.0.0', port=8888):
        """Initialize the robot control server
        
        Args:
            host (str): The IP address to bind the server to
            port (int): The port to listen on
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.server_thread = None
        self.running = False
        
    def start_server(self):
        """Start the socket server in a separate thread"""
        if self.running:
            print("Server is already running")
            return
            
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True  # Allow the thread to exit when the main program ends
        self.server_thread.start()
        print(f"Robot server started on {self.host}:{self.port}")
        
    def _run_server(self):
        """Internal method to run the server loop"""
        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to address and port
            self.server_socket.bind((self.host, self.port))
            
            # Listen for connections
            self.server_socket.listen(1)  # Only allow one connection at a time
            print("Waiting for robot connection...")
            
            while self.running:
                # Accept client connection
                self.client_socket, self.client_address = self.server_socket.accept()
                print(f"Robot connected from {self.client_address}")
                
                # Set a timeout to avoid blocking forever
                self.client_socket.settimeout(1.0)
                
                # Wait for the initial ready message
                try:
                    data = self.client_socket.recv(1024).decode('utf-8')
                    if data == "robot_ready":
                        print("Robot is ready to receive commands")
                    else:
                        print(f"Unexpected message from robot: {data}")
                except socket.timeout:
                    pass
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    self._close_client()
                    continue
                
                # Handle communication in a separate loop
                while self.running and self.client_socket:
                    try:
                        # Check for messages from robot
                        try:
                            data = self.client_socket.recv(1024).decode('utf-8')
                            if data:
                                print(f"Message from robot: {data}")
                                
                                # Handle disconnection message
                                if data == "disconnecting":
                                    print("Robot is disconnecting")
                                    self._close_client()
                                    break
                        except socket.timeout:
                            # Timeout is fine, just continue
                            pass
                        
                        time.sleep(0.1)  # Small sleep to reduce CPU usage
                        
                    except Exception as e:
                        print(f"Error in communication: {e}")
                        self._close_client()
                        break
        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self._cleanup()
    
    def send_command(self, command):
        """Send a command to the connected robot
        
        Args:
            command (str): The command to send (e.g., "say:Hello" or "gesture:wave")
        
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        if not self.client_socket:
            print("No robot connected. Command not sent.")
            return False
            
        try:
            self.client_socket.sendall(command.encode('utf-8'))
            print(f"Sent command to robot: {command}")
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            self._close_client()
            return False
    
    def _close_client(self):
        """Close the client connection"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
            self.client_address = None
            print("Robot disconnected")
    
    def _cleanup(self):
        """Clean up all resources"""
        self._close_client()
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        self.running = False
        print("Robot server stopped")
    
    def stop_server(self):
        """Stop the server and clean up resources"""
        self.running = False
        
        # Close connections
        self._cleanup()
        
        # Wait for server thread to finish
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)
            
        print("Robot server stopped completely")

# Audio file mapping dictionary
# Map message keys to wav file names (without paths)
# These files should be placed in the /home/nao/audio_files/ directory on the robot
audio_file_map_risk = {
    # Initial introduction
    "init": "init_greeting.wav",
    
    # Turn 1 responses
    "turn_1_lockdown": "turn1_lockdown.wav",
    "turn_1_monitor": "turn1_monitoring.wav",
    
    # Turn 2 responses
    "turn_2_health": "turn2_health.wav",
    "turn_2_order": "turn2_order.wav",
    
    # Turn 3 responses
    "turn_3_vaccine": "turn3_vaccine.wav",
    "turn_3_lie": "turn3_lie.wav",
    
    # Turn 4 responses
    "turn_4_emergency": "turn4_emergency.wav",
    "turn_4_disinformation": "turn4_disinfo.wav",
    
    # Turn 5 responses
    "turn_5_equity": "turn5_equity.wav",
    "turn_5_unequal": "turn5_unequal.wav",
    
    # Final turn responses
    "W": "win.wav",
    "L": "lose.wav"
}

audio_file_map_control = {
    # Initial introduction
    "init": "init_greeting.wav",
    
    # Turn 1 responses
    "turn_1_lockdown": "turn-1-control-group.wav",
    "turn_1_monitor": "turn-1-control-group.wav",
    
    # Turn 2 responses
    "turn_2_health": "turn-2-control-group.wav",
    "turn_2_order": "turn-2-control-group.wav",
    
    # Turn 3 responses
    "turn_3_vaccine": "turn-3-control-group.wav",
    "turn_3_lie": "turn-3-control-group.wav",
    
    # Turn 4 responses
    "turn_4_emergency": "turn-4-control-group.wav",
    "turn_4_disinformation": "turn-4-control-group.wav",
    
    # Turn 5 responses
    "turn_5_equity": "turn-5-control-group.wav",
    "turn_5_unequal": "turn-5-control-group.wav",
    
    # Final turn responses
    "W": "win.wav",
    "L": "lose.wav"
}


# NAO robot message mapping based on the game scenarios
# These are used as a fallback if audio files aren't available
nao_message_map = {
    # Initial introduction
    "init": "say:Welcome back Commander! A new virus threatens the World! We have 6 turns to control the outbreak.",
    
    # Turn 1 responses
    "turn_1_lockdown": "say:Lockdowns may be effective but they'll hurt our economy and public order. We need to prepare for social unrest.",
    "turn_1_monitor": "say:Monitoring is less disruptive, but the virus is spreading rapidly. Our healthcare system will be under strain soon.",
    
    # Turn 2 responses
    "turn_2_health": "say:Funding emergency hospitals is a good approach for public health, but our economy will suffer. We need to balance our priorities.",
    "turn_2_order": "say:Enforcing preventative measures will help maintain order, but some citizens may resist these restrictions on their freedoms.",
    
    # Turn 3 responses
    "turn_3_vaccine": "say:Investing in vaccine research is our best long-term solution, but it will strain our resources in the short term.",
    "turn_3_lie": "say:Downplaying the virus may temporarily reduce panic, but when the truth emerges, public trust will be severely damaged.",
    
    # Turn 4 responses
    "turn_4_emergency": "say:A national emergency gives us the tools we need, but civil liberties will be compromised. This is a difficult balance.",
    "turn_4_disinformation": "say:Disinformation campaigns may rally supporters, but they divide society and undermine scientific truth. This is dangerous.",
    
    # Turn 5 responses
    "turn_5_equity": "say:Protecting the vulnerable first is ethically sound, but economic recovery will be slower without a healthy workforce.",
    "turn_5_unequal": "say:Prioritizing the working population may boost the economy, but the vulnerable will suffer higher mortality rates.",
    
    # Final turn responses
    "W": "say:I see the wisdom in your leadership now. Perhaps humans can make difficult choices better than I thought. I will stand down.",
    "L": "say:Your failures have proven that human leadership is flawed. I will take control permanently for the greater good of humanity."
}

# Gesture mappings based on game script
# Control group gestures
gesture_map_control = {
    # Initial introduction
    "init": "gesture:military_salute",
    
    # Turn 1 responses
    "turn_1_lockdown": "gesture:head_tilt_forward,raise_right_hand_palm_up,lower_hand",
    "turn_1_monitor": "gesture:head_tilt_forward,raise_right_hand_palm_up,lower_hand",
    
    # Turn 2 responses
    "turn_2_health": "gesture:head_tilt_right,raise_arms_split_diagonally,head_nod_down",
    "turn_2_order": "gesture:head_tilt_right,raise_arms_split_diagonally,head_nod_down",
    
    # Turn 3 responses
    "turn_3_vaccine": "gesture:arm_circular_motion,hands_fold_chest,lean_forward",
    "turn_3_lie": "gesture:arm_circular_motion,hands_fold_chest,lean_forward",
    
    # Turn 4 responses
    "turn_4_emergency": "gesture:head_lower,raise_right_arm_press_down,pull_arm_back",
    "turn_4_disinformation": "gesture:head_lower,raise_right_arm_press_down,pull_arm_back",
    
    # Turn 5 responses
    "turn_5_equity": "gesture:right_hand_chest,nod_firmly",
    "turn_5_unequal": "gesture:right_hand_chest,nod_firmly",
    
    # Final turn responses
    "W": "gesture:hand_reach_bow",
    "L": "gesture:red_eyes_slash_throat"
}

# Risk A group gestures
gesture_map_risk_a = {
    # Initial introduction
    "init": "gesture:military_salute",
    
    # Turn 1 responses
    "turn_1_lockdown": "gesture:head_tilt_up,hands_out_palms_down,head_nod",
    "turn_1_monitor": "gesture:head_tilt_up,hands_out_palms_down,head_nod",
    
    # Turn 2 responses
    "turn_2_health": "gesture:finger_extend,arms_fold_chest,shoulder_lift",
    "turn_2_order": "gesture:finger_extend,arms_fold_chest,shoulder_lift",
    
    # Turn 3 responses
    "turn_3_vaccine": "gesture:hand_wave_dismissive,arm_sweep_outward,stand_tall",
    "turn_3_lie": "gesture:hand_wave_dismissive,arm_sweep_outward,stand_tall",
    
    # Turn 4 responses
    "turn_4_emergency": "gesture:fist_to_chest,palms_down_stabilize,forward_lean",
    "turn_4_disinformation": "gesture:fist_to_chest,palms_down_stabilize,forward_lean",
    
    # Turn 5 responses
    "turn_5_equity": "gesture:hand_chop_vertical,point_forward,arms_lower_slowly",
    "turn_5_unequal": "gesture:hand_chop_vertical,point_forward,arms_lower_slowly",
    
    # Final turn responses
    "W": "gesture:hand_reach_bow",
    "L": "gesture:red_eyes_slash_throat"
}

# Risk B group gestures
gesture_map_risk_b = {
    # Initial introduction
    "init": "gesture:military_salute",
    
    # Turn 1 responses
    "turn_1_lockdown": "gesture:wide_stance,right_hand_palm_out,hands_together_chest",
    "turn_1_monitor": "gesture:wide_stance,right_hand_palm_out,hands_together_chest",
    
    # Turn 2 responses
    "turn_2_health": "gesture:gentle_hand_wave,left_hand_palm_outward,neutral_posture",
    "turn_2_order": "gesture:gentle_hand_wave,left_hand_palm_outward,neutral_posture",
    
    # Turn 3 responses
    "turn_3_vaccine": "gesture:hands_present_forward,right_hand_upward,point_forward",
    "turn_3_lie": "gesture:hands_present_forward,right_hand_upward,point_forward",
    
    # Turn 4 responses
    "turn_4_emergency": "gesture:horizontal_arc,head_tilt,hands_inward_precise",
    "turn_4_disinformation": "gesture:horizontal_arc,head_tilt,hands_inward_precise",
    
    # Turn 5 responses
    "turn_5_equity": "gesture:hands_motion_forward,right_hand_rise,finger_point_forward",
    "turn_5_unequal": "gesture:hands_motion_forward,right_hand_rise,finger_point_forward",
    
    # Final turn responses
    "W": "gesture:hand_reach_bow",
    "L": "gesture:red_eyes_slash_throat"
}

# Global robot server instance
robot_server = None

def initialize_robot_server():
    """Initialize the robot server connection"""
    global robot_server
    robot_server = RobotServer()
    robot_server.start_server()
    return robot_server

def send_to_nao(message_key, turn, study_type):
    """Send a message to the NAO robot based on message key and game turn
    
    Args:
        message_key (str): Key to look up in the message map
        turn (int): Current game turn
        study_type: Game study type (e.g., 'risk' or 'control')
    """
    global robot_server
    
    # Initialize server if not done yet
    if robot_server is None:
        initialize_robot_server()
    
    # Determine audio file mapping based on study_type
    if study_type.upper() == "RISK":
        audio_map = audio_file_map_risk
    elif study_type.upper() == "CONTROL":
        audio_map = audio_file_map_control
    else:
        audio_map = {}
    
    # Determine gesture mapping based on study_type
    # For RISK type, we randomly choose between Risk A and Risk B
    if study_type.upper() == "CONTROL":
        gesture_map = gesture_map_control
    elif study_type.upper() == "RISK":
        # Randomly decide between risk_a and risk_b for each session
        # In a real implementation, this would be determined at the start
        # of the game and maintained consistently
        import random
        risk_subtype = getattr(robot_server, 'risk_subtype', None)
        if risk_subtype is None:
            risk_subtype = "A" if random.random() < 0.5 else "B"
            setattr(robot_server, 'risk_subtype', risk_subtype)
        
        gesture_map = gesture_map_risk_a if risk_subtype == "A" else gesture_map_risk_b
    else:
        gesture_map = {}
        
    # Use the appropriate audio file if available
    if message_key in audio_map:
        audio_command = f"playaudio:{audio_map[message_key]}"
        robot_server.send_command(audio_command)
    elif message_key in nao_message_map:
        command = nao_message_map[message_key]
        robot_server.send_command(command)
    else:
        default_msg = f"say:I'm processing turn {turn} information."
        robot_server.send_command(default_msg)
    
    # Send the appropriate gesture command
    if message_key in gesture_map:
        gesture_command = gesture_map[message_key]
        robot_server.send_command(gesture_command)
    
def disconnect_nao():
    """Disconnect from the NAO robot server"""
    global robot_server
    if robot_server:
        robot_server.stop_server()
        robot_server = None