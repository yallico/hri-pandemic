# NAO Pandemic Game Socket Communication

This system enables communication between the Ren'Py pandemic simulation game and a NAO robot through a socket server.

## Components

1. **nao_server.py** - Socket server that connects the game and NAO
2. **nao_client.py** - Client script to run on or with the NAO robot
3. **nao_comms.rpy** - Ren'Py module to handle communication with the server
4. **script.rpy** - Main game script, modified to send messages to NAO after each turn

## Setup and Usage

### 1. Start the Server

First, start the socket server which will relay messages between the game and NAO:

```bash
python nao_server.py
```

The server will start and listen on:
- Port 9999 for the Ren'Py game
- Port 9998 for the NAO robot

### 2. Connect the NAO Robot

Option A: Run the client script on the NAO robot:
```bash
python nao_client.py <server_ip> 9998
```

Option B: Run the client script on your computer to test:
```bash
python nao_client.py localhost 9998
```

### 3. Run the Game

Start the Ren'Py game. It will automatically connect to the socket server when it starts, and send messages to NAO after each turn in the game.

## Message Flow

1. Game user makes a choice in Ren'Py
2. Ren'Py sends a message to the socket server with the turn number and text
3. Socket server forwards the message to the NAO robot
4. NAO robot speaks the text
5. NAO robot sends acknowledgment back to the server
6. Server sends acknowledgment back to the game

## Customizing NAO Responses

To customize what NAO says after each turn, edit the `nao_speech_messages` dictionary in `script.rpy`.

## Troubleshooting

- Check the log files: `nao_server.log` and `nao_client.log`
- Make sure firewalls allow connections on ports 9998 and 9999
- If connection fails, restart the server and clients

## Dependencies

- Python 3.6+ for the server and client (if not running on NAO)
- Python 2.7 with NAOqi SDK for the client (if running on NAO)
- Ren'Py game engine 