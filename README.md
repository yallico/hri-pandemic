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

### Step 2: Prepare Audio Files (Optional)

For better speech quality, you can use pre-recorded audio files:

1. Create WAV audio files for robot speech (sample rate: 22050Hz for European languages, 16000Hz for Asian languages, format: S16_LE, 1 channel)
2. Name the files according to the mapping in `src/game/robotcontrol.py` (e.g., `init_greeting.wav`, `turn1_lockdown.wav`, etc.)
3. Transfer these files to the NAO robot in the `/home/nao/audio_files/` directory
4. If this directory doesn't exist, the system will attempt to create it automatically

If audio files are not available, the system will fall back to using text-to-speech.

### Step 3: Launch the Renpy Game

1. Navigate to your Renpy game directory
2. Launch the game using the Renpy launcher
3. The game will automatically start the socket server when it begins

### Step 4: Run the Robot Behavior

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
- Support for pre-recorded audio files for higher quality speech
- Automatic audio file generation using TTS when needed
- Automatic reconnection if the connection is lost
- Graceful shutdown when the game ends

## Troubleshooting

- **Connection Issues**: Ensure both the game and robot are on the same network
- **TTS Errors**: If speech doesn't work, check that NAOqi services are running
- **Audio File Issues**: Verify WAV files are in the correct format (22050Hz, S16_LE, 1 channel)
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

/home/nao/audio_files/         # Directory on the NAO robot for audio files
  ├── init_greeting.wav        # Audio file for initial greeting
  ├── turn1_lockdown.wav       # Audio file for lockdown response
  └── ... (other audio files)
```

## How It Works

The game establishes a socket server connection that the robot connects to. When key events occur in the game, it sends commands to the robot, primarily to make it speak and provide advice to the player.

The integration uses a simple command protocol:
- `playaudio:filename.wav` to play a specific audio file
- `say:text` to make the robot speak (fallback if audio file not available)
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