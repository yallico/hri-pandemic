# NAO Robot Integration for Pandemic Game

This guide explains how the Renpy game integrates with a NAO or Pepper robot to enhance the gameplay experience.

## Components

1. **robotcontrol.py**: A Python module that sets up socket communication between the Renpy game and the NAO robot.
2. **renpy_behavior.xar**: A Choregraphe behavior file that runs on the robot to receive and process commands from the game.

## How It Works

The system uses a client-server architecture:
- The Renpy game acts as a server (through robotcontrol.py)
- The NAO robot acts as a client (through the Python box in Choregraphe)

When events happen in the game, commands are sent to the robot that trigger appropriate behaviors, primarily speech responses that match what's happening in the game.

## Setup Instructions

### Step 1: Robot Setup (Choregraphe)

1. Open Choregraphe and connect to your robot (or virtual robot)
2. Open the `renpy_behavior.xar` file in Choregraphe
3. If using a physical robot, update the IP address in the script:
   ```python
   self.session.connect("tcp://YOUR_ROBOT_IP:9559")
   ```
4. Run the behavior

### Step 2: Run the Game

1. Launch the Renpy game
2. The game will automatically:
   - Initialize the socket server when it starts
   - Accept a connection from the robot
   - Send commands to the robot at appropriate moments during gameplay

## Message Flow

1. When the game starts, the robotcontrol module initializes the server and waits for a connection
2. The robot connects to the game and sends a "robot_ready" message
3. At key story points, the game calls `send_to_nao(message_key, turn)` to trigger robot behaviors
4. When the game ends, it calls `nao_disconnect()` to cleanly close the connection

## Customizing Robot Responses

The robot responses are defined in the `nao_message_map` dictionary in `robotcontrol.py`. Each message has a key and a corresponding command:

```python
nao_message_map = {
    "init": "say:Welcome back Commander!...",
    "A": "say:Lockdowns may be effective but...",
    # more messages...
}
```

To modify or add new responses:
1. Add a new entry to this dictionary
2. Use one of the supported command formats:
   - `say:Your text here` - Makes the robot speak
   - `gesture:animation_name` - Makes the robot perform an animation
   - `posture:posture_name` - Changes the robot's posture
   - `move:x,y,theta` - Moves the robot

## Troubleshooting

### Connection Issues
- Make sure both the computer and robot are on the same network
- Check that port 8888 is not blocked by a firewall
- Verify the IP addresses are correct

### Robot Not Responding
- Check if the correct behavior is running on the robot
- Look for error messages in the Choregraphe console
- Restart both the game and the robot behavior

### Game Crashes
- Check the Renpy console for error messages
- Verify that the robotcontrol.py file is in the correct location 