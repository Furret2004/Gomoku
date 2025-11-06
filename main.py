"""
Gomoku Menu
Main entry point - choose between AI and multiplayer modes
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from src.game_state import GameStateManager
from src.game_statistics import GameStatistics


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
        
        # Continue button (only show if save exists)
        if GameStateManager.has_saved_game():
            continue_button = tk.Button(
                button_frame,
                text="▶️ Continue Game",
                command=self.continue_game,
                font=('Arial', 14, 'bold'),
                width=20,
                height=2,
                bg='#27AE60',
                fg='white',
                activebackground='#229954',
                activeforeground='white',
                cursor='hand2',
                relief=tk.RAISED,
                bd=3
            )
            continue_button.pack(pady=10)
        
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
        
        # Statistics button
        stats_button = tk.Button(
            button_frame,
            text="📊 Statistics",
            command=self.show_statistics,
            font=('Arial', 10),
            width=20,
            bg='#9B59B6',
            fg='white',
            activebackground='#8E44AD',
            activeforeground='white',
            cursor='hand2'
        )
        stats_button.pack(pady=10)
        
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
        
    def continue_game(self):
        """Continue saved game"""
        # Show save info
        info = GameStateManager.get_save_info()
        if info:
            message = (
                f"Saved game found:\n\n"
                f"Date: {info['timestamp'][:19]}\n"
                f"Difficulty: {info['ai_difficulty']}\n"
                f"Current Player: {info['current_player']}\n\n"
                f"Continue this game?"
            )
            response = messagebox.askyesno("Continue Game", message, icon='question')
            if not response:
                return
        
        self.root.destroy()
        # Import and run AI game with load
        from singleplayer import GomokuSinglePlayer
        game = GomokuSinglePlayer()
        game.load_game()
        game.run()
    
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
    
    def show_statistics(self):
        """Show game statistics"""
        stats = GameStatistics()
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Game Statistics")
        stats_window.geometry("600x500")
        stats_window.resizable(False, False)
        stats_window.configure(bg='#2C3E50')
        
        # Title
        title_label = tk.Label(
            stats_window,
            text="Your Game Statistics",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2C3E50',
            pady=10
        )
        title_label.pack()
        
        # Statistics text
        stats_text = scrolledtext.ScrolledText(
            stats_window,
            width=70,
            height=20,
            font=('Courier', 10),
            wrap=tk.WORD,
            bg='#ECF0F1'
        )
        stats_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Insert statistics
        summary = stats.get_statistics_summary()
        stats_text.insert(tk.END, summary)
        stats_text.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(
            stats_window,
            text="Close",
            command=stats_window.destroy,
            font=('Arial', 12),
            bg='#3498DB',
            fg='white',
            width=15
        )
        close_button.pack(pady=10)
        
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
