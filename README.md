# Gomoku - Online Multiplayer Game

A Python implementation of Gomoku (Five in a Row) with **single-player AI** and **online multiplayer** modes using socket programming and a graphical user interface.

## 🎮 Game Description

Gomoku is a classic strategy board game where two players take turns placing stones on a 15x15 grid. The first player to get exactly five stones in a row (horizontally, vertically, or diagonally) wins the game!

### Features

- 🤖 **Single Player vs AI**: Play against a random AI opponent
- 🌐 **Online Multiplayer**: Play against opponents over the network
- 🎨 **GUI Interface**: Clean and intuitive tkinter-based interface
- 🎯 **Main Menu**: Easy-to-use menu to choose game mode
- 🔄 **Automatic Matchmaking**: Server automatically pairs waiting players
- ♟️ **Classic Gomoku Rules**: 15x15 board with five-in-a-row winning condition
- 🎯 **Real-time Updates**: Instant move synchronization between players

## 📋 Requirements

- Python 3.7 or higher
- tkinter (usually comes with Python)

No additional packages required! The game uses only Python standard library.

## 🚀 How to Run

### Quick Start (Recommended)

**Start the game with the main menu:**

```bash
python main.py
```

Then choose:
- **🤖 Play vs AI** - Single player game against computer
- **👥 Play vs Player** - Online multiplayer (requires server)

### For Multiplayer Mode

**Step 1: Start the server (in a separate terminal):**

```bash
python start_server.py
```

Or navigate to the network folder:
```bash
cd src/network
python server.py
```

The server will start on `0.0.0.0:5555` and wait for connections.

**Step 2: Run the game and choose multiplayer:**

```bash
python main.py
```

Click **"👥 Play vs Player"** and enter the server IP address:
- For local testing: use `127.0.0.1` or `localhost`
- For network play: use the server's IP address on your network

**Step 3: Play!**

1. Wait for another player to connect
2. When both players are connected, the game starts automatically
3. Player X (black stones) goes first
4. Click on the board to place your stone
5. First to get 5 in a row wins!

## 🎯 Game Rules

1. **Board**: 15x15 grid
2. **Players**: Two players (X with black stones, O with white stones)
3. **Turns**: Players alternate placing stones
4. **Winning**: Get exactly 5 stones in a row (horizontal, vertical, or diagonal)
5. **No Take-backs**: Once a stone is placed, it cannot be moved

## 🏗️ Project Structure

```
gomoku/
├── main.py              # Main menu - START HERE!
├── singleplayer.py      # Single player vs AI mode
├── start_server.py      # Easy server launcher
├── src/
│   ├── game.py          # Core game logic and rules
│   ├── ai.py            # AI opponent logic
│   └── network/
│       ├── server.py    # Network server handling multiple games
│       └── client.py    # GUI client with networking
├── assets/              # Game assets
└── README.md            # This file
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
