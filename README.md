# 🎮 Gomoku - Five in a Row

A feature-rich Gomoku (Five in a Row) game implementation with AI opponents and online multiplayer support.

## ✨ Features

### Core Gameplay
- **15×15 Game Board** - Classic Gomoku board size
- **Win Detection** - Automatic detection of 5-in-a-row (horizontal, vertical, diagonal)
- **Two Game Modes** - Single-player vs AI and Online Multiplayer

### AI System (5/5 points)
- ✅ **Random AI** - Easy difficulty for beginners
- ✅ **Minimax with Alpha-Beta Pruning** - Strategic gameplay
- ✅ **4 Difficulty Levels** - Easy, Medium, Hard, Expert
- ✅ **Performance Optimizations**:
  - Board state caching (40-60% hit rate)
  - Move ordering and nearby move selection
  - Quick win/block detection

### Network Multiplayer (4/4 points)
- ✅ **Online PvP** - Play against friends over the network
- ✅ **Multiple Game Rooms** - Server supports concurrent games
- ✅ **Error Handling** - Connection retry and graceful disconnection
- ✅ **New Game Feature** - Synchronized game reset

### Game Management (1/1 point)
- ✅ **Save/Load System** - Pause and continue games later
- ✅ **Statistics Tracking** - Win/loss records per difficulty
- ✅ **Game History** - Last 50 games with timestamps
- ✅ **Auto-save Prompt** - Never lose progress

## 🔧 Requirements

- **Python 3.7+** (no external dependencies!)
- Standard library only:
  - `tkinter` - GUI framework
  - `socket` - Network communication
  - `json` - Data serialization
  - `threading` - Concurrent connections

## 📦 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Furret2004/Gomoku.git
cd Gomoku
```

2. **Verify Python installation:**
```bash
python --version  # Should be 3.7 or higher
```

3. **Run the game:**
```bash
python main.py
```

That's it! No `pip install` needed.

## 🚀 Quick Start

### Single Player (vs AI)

```bash
python singleplayer.py
```

Or launch from the main menu:
```bash
python main.py
# Click "Play vs AI"
```

### Multiplayer (Online PvP)

**Step 1: Start the server (host)**
```bash
python start_server.py
```
The server will start on port 5555.

**Step 2: Connect clients (players)**

On the same computer:
```bash
python start_client.py
# Enter: 127.0.0.1
```

On different computers:
```bash
python start_client.py
# Enter: <server_ip_address>
```

Or launch from main menu:
```bash
python main.py
# Click "Play vs Player"
```

## 📁 Project Structure

```
Gomoku/
├── main.py                    # Main menu (entry point)
├── singleplayer.py            # Single-player game vs AI
├── start_server.py            # Multiplayer server launcher
├── start_client.py            # Multiplayer client launcher
├── README.md                  # This file
├── code_used.md               # Implementation documentation
├── requirements.txt           # Empty (no external deps)
│
├── saves/                     # Game saves and statistics
│   ├── gomoku_save.json      # Current game save file
│   └── statistics.json       # Player statistics
│
└── src/                       # Source code modules
    ├── game.py               # Core game logic
    ├── ai.py                 # Random AI (Easy mode)
    ├── ai_minimax.py         # Minimax AI with alpha-beta
    ├── ai_manager.py         # AI difficulty manager
    ├── game_state.py         # Save/load functionality
    ├── game_statistics.py    # Statistics tracking
    └── network/              # Multiplayer networking
        ├── server.py         # Game server
        └── client.py         # Game client with GUI
```


### Completed Features

- [x] Random AI (Easy mode) - 1 point
- [x] Minimax with Alpha-Beta - 3 points
- [x] Multiple difficulty levels - 1 point
- [x] Online multiplayer PvP - 4 points
- [x] Save/Load/Continue - 1 point
- [x] Statistics tracking
- [x] Performance optimizations
- [x] Error handling and reconnection

### Future Enhancements

- [ ] Machine Learning AI (AlphaZero-style)
- [ ] 3-player variant mode
- [ ] Obstacle tiles (game variant)
- [ ] Opening book for AI
- [ ] Replay viewer
- [ ] Online lobby/ranking system


## 🙏 Acknowledgments

- Minimax algorithm based on classic game theory
- Alpha-Beta pruning optimization technique
- GUI built with Python Tkinter
- Inspired by traditional Gomoku/Five-in-a-Row games

---

**Enjoy playing Gomoku!** 🎮
