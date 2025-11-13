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
        self.root.geometry("400x500")
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
        button_frame.pack(pady=20)
        
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
        
    def start_ai_game(self):
        """Start single player game vs AI - show New/Continue dialog first"""
        # Check if saved game exists
        has_save = GameStateManager.has_saved_game()
        
        if has_save:
            # Show New Game / Continue Game dialog
            choice = self.show_new_or_continue_dialog()
            
            if choice is None:  # User cancelled
                return
            elif choice == "continue":
                self.continue_saved_game()
            else:  # choice == "new"
                self.start_new_ai_game()
        else:
            # No save exists, go directly to new game
            self.start_new_ai_game()
    
    def show_new_or_continue_dialog(self):
        """
        Show dialog to choose between New Game or Continue Game
        
        Returns:
            'new', 'continue', or None if cancelled
        """
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Play vs AI")
        dialog.geometry("400x500")
        dialog.resizable(False, False)
        dialog.configure(bg='#2C3E50')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Variable to store choice
        choice = [None]
        
        # Title
        title_label = tk.Label(
            dialog,
            text="Play vs AI",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2C3E50'
        )
        title_label.pack(pady=30)
        
        # Button frame
        button_frame = tk.Frame(dialog, bg='#2C3E50')
        button_frame.pack(pady=20)
        
        def on_choice(c):
            choice[0] = c
            dialog.destroy()
        
        # New Game button
        new_button = tk.Button(
            button_frame,
            text="🎮 New Game",
            command=lambda: on_choice("new"),
            font=('Arial', 14, 'bold'),
            width=18,
            height=2,
            bg='#3498DB',
            fg='white',
            activebackground='#2980B9',
            activeforeground='white',
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        new_button.pack(pady=10)
        
        # Continue Game button - only show if save actually exists
        if GameStateManager.has_saved_game():
            continue_button = tk.Button(
                button_frame,
                text="▶️ Continue Game",
                command=lambda: on_choice("continue"),
                font=('Arial', 14, 'bold'),
                width=18,
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
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=('Arial', 10),
            width=18,
            bg='#95A5A6',
            fg='white',
            activebackground='#7F8C8D',
            activeforeground='white',
            cursor='hand2'
        )
        cancel_button.pack(pady=20)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        return choice[0]
    
    def start_new_ai_game(self):
        """Start a new AI game - show difficulty selection"""
        # Show difficulty selection dialog
        difficulty = self.show_difficulty_dialog()
        
        if difficulty is None:  # User cancelled
            return
        
        self.root.destroy()
        # Import and run AI game with selected difficulty
        from singleplayer import GomokuSinglePlayer
        game = GomokuSinglePlayer(difficulty=difficulty)
        game.run()
    
    def continue_saved_game(self):
        """Continue saved game - load directly"""
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
    
    def show_difficulty_dialog(self):
        """
        Show a dialog to select AI difficulty
        
        Returns:
            Selected difficulty string or None if cancelled
        """
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Select AI Difficulty")
        dialog.geometry("400x600")
        dialog.resizable(False, False)
        dialog.configure(bg='#2C3E50')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Variable to store selection
        selected_difficulty = [None]
        
        # Title
        title_label = tk.Label(
            dialog,
            text="Choose Difficulty",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2C3E50'
        )
        title_label.pack(pady=20)
        
        # Button frame
        button_frame = tk.Frame(dialog, bg='#2C3E50')
        button_frame.pack(pady=20, fill=tk.BOTH, expand=True, padx=30)
        
        # Difficulty options from AIManager
        from src.ai_manager import AIManager
        difficulties = AIManager.get_difficulty_list()
        
        # Color scheme for buttons
        colors = {
            'Easy': ('#27AE60', '#229954'),      # Green
            'Medium': ('#F39C12', '#D68910'),    # Orange
            'Hard': ('#E74C3C', '#C0392B'),      # Red
            'Expert': ('#8E44AD', '#7D3C98')     # Purple
        }
        
        def on_difficulty_select(diff):
            selected_difficulty[0] = diff
            dialog.destroy()
        
        # Create button for each difficulty
        for difficulty in difficulties:
            description = AIManager.get_description(difficulty)
            bg_color, active_color = colors.get(difficulty, ('#3498DB', '#2980B9'))
            
            # Container frame for button and description
            container = tk.Frame(button_frame, bg='#2C3E50')
            container.pack(pady=8, fill=tk.X)
            
            # Difficulty button
            btn = tk.Button(
                container,
                text=difficulty,
                command=lambda d=difficulty: on_difficulty_select(d),
                font=('Arial', 14, 'bold'),
                width=18,
                height=2,
                bg=bg_color,
                fg='white',
                activebackground=active_color,
                activeforeground='white',
                cursor='hand2',
                relief=tk.RAISED,
                bd=3
            )
            btn.pack()
            
            # Description label
            desc_label = tk.Label(
                container,
                text=description,
                font=('Arial', 9, 'italic'),
                fg='#BDC3C7',
                bg='#2C3E50'
            )
            desc_label.pack(pady=2)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=('Arial', 10),
            width=18,
            bg='#95A5A6',
            fg='white',
            activebackground='#7F8C8D',
            activeforeground='white',
            cursor='hand2'
        )
        cancel_button.pack(pady=15)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        return selected_difficulty[0]
        
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
