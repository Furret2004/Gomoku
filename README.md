# Gomoku - Online Multiplayer Game

A Python implementation of Gomoku (Five in a Row) with online multiplayer support using socket programming and a graphical user interface.

## 🎮 Game Description

Gomoku is a classic strategy board game where two players take turns placing stones on a 15x15 grid. The first player to get exactly five stones in a row (horizontally, vertically, or diagonally) wins the game!

### Features

- 🌐 **Online Multiplayer**: Play against opponents over the network
- 🎨 **GUI Interface**: Clean and intuitive tkinter-based interface
- 🔄 **Automatic Matchmaking**: Server automatically pairs waiting players
- ♟️ **Classic Gomoku Rules**: 15x15 board with five-in-a-row winning condition
- 🎯 **Real-time Updates**: Instant move synchronization between players

## 📋 Requirements

- Python 3.7 or higher
- tkinter (usually comes with Python)

No additional packages required! The game uses only Python standard library.

## 🚀 How to Run

### Step 1: Start the Server

First, start the game server. This needs to be running before any clients can connect.

```bash
python server.py
```

The server will start on `0.0.0.0:5555` and wait for connections.

### Step 2: Start the Client(s)

Open a new terminal and start the client:

```bash
python client.py
```

When prompted, enter the server IP address:
- For local testing: use `127.0.0.1` or `localhost`
- For network play: use the server's IP address on your network

### Step 3: Connect and Play

1. Click "Connect to Server" button
2. Wait for another player to connect
3. When both players are connected, the game starts automatically
4. Player X (black stones) goes first
5. Click on the board to place your stone
6. First to get 5 in a row wins!

## 🎯 Game Rules

1. **Board**: 15x15 grid
2. **Players**: Two players (X with black stones, O with white stones)
3. **Turns**: Players alternate placing stones
4. **Winning**: Get exactly 5 stones in a row (horizontal, vertical, or diagonal)
5. **No Take-backs**: Once a stone is placed, it cannot be moved

## 🏗️ Project Structure

```
gomoku/
├── game.py       # Core game logic and rules
├── server.py     # Network server handling multiple games
├── client.py     # GUI client with networking
└── README.md     # This file
```

## 🔧 Advanced Usage

### Running Server on Different Port

Edit `server.py` and change the port number:

```python
server = GameServer(host='0.0.0.0', port=YOUR_PORT)
```

Also update `client.py` to match:

```python
client = GomokuClient(host=host, port=YOUR_PORT)
```

### Playing Over the Internet

1. Port forward port 5555 on your router to the server machine
2. Find your public IP address
3. Clients connect using your public IP address

**Note**: For internet play, consider security implications and use a VPN or secure connection.

## 🐛 Troubleshooting

### "Connection refused" error
- Make sure the server is running first
- Check that you're using the correct IP address
- Verify firewall isn't blocking the connection

### "Address already in use" error
- Another instance of the server is already running
- Wait a moment and try again, or restart your computer

### Game doesn't respond
- Check your network connection
- Restart both server and client

## 🎓 How It Works

### Architecture

1. **Server**: Manages game state and coordinates between players
   - Handles matchmaking (pairs waiting players)
   - Validates moves
   - Detects win conditions
   - Synchronizes game state between clients

2. **Client**: Provides GUI and communicates with server
   - Displays game board
   - Sends moves to server
   - Receives and displays opponent moves
   - Shows game status

3. **Game Module**: Contains core game logic
   - Board management
   - Move validation
   - Win detection algorithm

### Network Protocol

Communication uses JSON messages over TCP sockets:
- `waiting`: Player is waiting for opponent
- `start`: Game is starting
- `move`: Player makes a move
- `opponent_move`: Opponent made a move
- `game_over`: Game has ended
- `reset`: Start a new game

## 🤝 Contributing

Feel free to fork this project and add your own features! Some ideas:
- Add chat functionality
- Implement game replay
- Add AI opponent
- Create game lobbies with multiple rooms
- Add player statistics

## 📝 License

This project is open source and available for educational purposes.

## 👥 Credits

Created as a demonstration of network programming with Python sockets and GUI development with tkinter.

Enjoy playing Gomoku! 🎉
