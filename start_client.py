"""
Start Gomoku Client
Run this to connect to a multiplayer game
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.network.client import GomokuClient


if __name__ == "__main__":
    print("=" * 50)
    print("GOMOKU MULTIPLAYER CLIENT")
    print("=" * 50)
    
    # Get server address from user
    root = tk.Tk()
    root.withdraw()
    
    host = simpledialog.askstring(
        "Server Address",
        "Enter server IP address\n(leave empty for localhost):",
        initialvalue="127.0.0.1"
    )
    
    if host is None:
        print("[CLIENT] Connection cancelled by user")
        exit()
    
    if not host:
        host = "127.0.0.1"
    
    root.destroy()
    
    print(f"[CLIENT] Connecting to {host}:5555...")
    
    # Start client
    try:
        client = GomokuClient(host=host, port=5555)
        client.run()
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
        input("Press Enter to exit...")
