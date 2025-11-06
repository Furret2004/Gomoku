"""
Gomoku Menu
Main entry point - choose between AI and multiplayer modes
"""

import tkinter as tk
from tkinter import simpledialog
import subprocess
import sys
import os


class GomokuMenu:
    """Main menu for Gomoku game"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gomoku - Main Menu")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg='#2C3E50')
        
        self.create_menu()
        
    def create_menu(self):
        """Create the main menu UI"""
        # Title
        title_label = tk.Label(
            self.root,
            text="GOMOKU",
            font=('Arial', 32, 'bold'),
            fg='white',
            bg='#2C3E50'
        )
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(
            self.root,
            text="Five in a Row",
            font=('Arial', 14),
            fg='#BDC3C7',
            bg='#2C3E50'
        )
        subtitle_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#2C3E50')
        button_frame.pack(pady=40)
        
        # Play vs AI button
        ai_button = tk.Button(
            button_frame,
            text="🤖 Play vs AI",
            command=self.start_ai_game,
            font=('Arial', 14, 'bold'),
            width=20,
            height=2,
            bg='#3498DB',
            fg='white',
            activebackground='#2980B9',
            activeforeground='white',
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        ai_button.pack(pady=10)
        
        # Play vs Player button
        pvp_button = tk.Button(
            button_frame,
            text="👥 Play vs Player",
            command=self.start_multiplayer_game,
            font=('Arial', 14, 'bold'),
            width=20,
            height=2,
            bg='#E74C3C',
            fg='white',
            activebackground='#C0392B',
            activeforeground='white',
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        pvp_button.pack(pady=10)
        
        # Quit button
        quit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.quit_game,
            font=('Arial', 10),
            width=20,
            bg='#95A5A6',
            fg='white',
            activebackground='#7F8C8D',
            activeforeground='white',
            cursor='hand2'
        )
        quit_button.pack(pady=15)
        
    def start_ai_game(self):
        """Start single player game vs AI"""
        self.root.destroy()
        # Import and run AI game
        from singleplayer import GomokuSinglePlayer
        game = GomokuSinglePlayer()
        game.run()
        
    def start_multiplayer_game(self):
        """Start multiplayer game"""
        self.root.withdraw()
        
        # Ask for server address
        host = simpledialog.askstring(
            "Server Address",
            "Enter server IP address\n(leave empty for localhost):",
            initialvalue="127.0.0.1",
            parent=self.root
        )
        
        if host is None:  # User cancelled
            self.root.deiconify()
            return
        
        if not host:
            host = "127.0.0.1"
        
        self.root.destroy()
        
        # Import and run multiplayer client
        from src.network.client import GomokuClient
        client = GomokuClient(host=host, port=5555)
        client.run()
        
    def quit_game(self):
        """Quit the application"""
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Run the menu"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.root.mainloop()


if __name__ == "__main__":
    menu = GomokuMenu()
    menu.run()
