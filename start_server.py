"""
Start Gomoku Server
Run this to host multiplayer games
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Now import from the network module
from src.network.server import GameServer

if __name__ == "__main__":
    print("=" * 50)
    print("GOMOKU MULTIPLAYER SERVER")
    print("=" * 50)
    server = GameServer()
    server.start()
