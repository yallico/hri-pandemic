# NAO Robot Integration with Renpy Pandemic Game

This project enables a NAO/Pepper robot to interact with a Renpy-based pandemic simulation game. The robot serves as an advisor, providing verbal feedback with expressive arm gestures.

## Setup Instructions

### Step 1: Configure Choregraphe

1. Open Choregraphe and create a new behavior
2. Drag a Python Box from the Box Libraries panel to the flow diagram workspace
3. Double-click the Python Box to edit its script
4. Copy the entire code from `python_script` file into the Python Box
5. Check the port number in the code:
   ```python
   # Connection parameters
   host = '127.0.0.1'  # Change to your computer's IP if not using localhost
   port = 8888         # Make sure this matches the Renpy game's port
   ```
6. If needed, modify the port number to match your configuration
7. Save the behavior

### Step 2: Launch the Renpy Game

1. Navigate to your Renpy game directory
2. Launch the game using the Renpy launcher
3. The game will automatically start the socket server when it begins

### Step 3: Run the Robot Behavior

1. Make sure your NAO/Pepper robot is powered on and connected to the network
2. If using a physical robot, update the connection string in the Python Box:
   ```python
   self.session.connect("tcp://YOUR_ROBOT_IP:9559")
   ```
3. If using the virtual robot, keep it as `"tcp://127.0.0.1:9559"`
4. In Choregraphe, connect to your robot (real or virtual)
5. Run the behavior by clicking the "Play" button

## Operation Sequence

For proper operation, follow this sequence:
1. Start the Renpy game first
2. Wait for the game to initialize
3. Start the robot behavior in Choregraphe
4. The robot should connect to the game and say "robot_ready"
5. Proceed with the game, and the robot will respond to game events

## Features

- The robot will provide spoken advice at key decision points
- Arm gestures accompany speech for more expressive communication
- Automatic reconnection if the connection is lost
- Graceful shutdown when the game ends

## Troubleshooting

- **Connection Issues**: Ensure both the game and robot are on the same network
- **TTS Errors**: If speech doesn't work, check that NAOqi services are running
- **Arm Movement Issues**: Make sure the robot has sufficient space to move its arms
- **Port Conflicts**: If port 8888 is already in use, change it in both the Python script and Renpy game

## Project Structure

```
src/
  ├── game/                    # Renpy game files
  │   ├── script.rpy           # Main game script
  │   └── robotcontrol.py      # Robot control module
  │
  └── robot/                   # Robot behavior files
      └── nao_robot_behavior.xar  # Choregraphe behavior file

python_script                  # Python code for the Choregraphe box
```

## How It Works

The game establishes a socket server connection that the robot connects to. When key events occur in the game, it sends commands to the robot, primarily to make it speak and provide advice to the player.

The integration uses a simple command protocol:
- `say:text` to make the robot speak
- `gesture:name` to make the robot perform an animation
- `posture:name` to set the robot's posture
- `move:x,y,theta` to move the robot

## Gameplay

The player takes on the role of a global leader managing a pandemic crisis. They must make decisions that balance:
- Health
- Economy
- Public Order

The NAO robot serves as an advisor, providing commentary on the player's decisions.

## Credits

This project was developed for the HRI course at the University of Bristol. 