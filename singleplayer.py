"""
Gomoku Single Player vs AI
Play against a computer opponent with GUI
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from src.game import GomokuGame
from src.ai_manager import AIManager
from src.game_state import GameStateManager
from src.game_statistics import GameStatistics


class GomokuSinglePlayer:
    """Single player Gomoku game with GUI"""
    
    def __init__(self, difficulty='Medium'):
        self.board_size = 15
        self.game = GomokuGame(self.board_size)
        
        self.player_symbol = 'X'  # Player is X (black)
        self.ai_symbol = 'O'      # AI is O (white)
        self.game_active = True
        
        # AI with difficulty level
        self.difficulty = difficulty
        self.ai = AIManager.get_ai(self.game, self.difficulty, self.ai_symbol)
        
        # Statistics tracker
        self.statistics = GameStatistics()
        
        # GUI
        self.root = tk.Tk()
        self.root.title("Gomoku - Single Player vs AI")
        self.root.resizable(False, False)
        
        self.cell_size = 40
        self.create_gui()
        
    def create_gui(self):
        """Create the GUI"""
        # Top frame for info
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        
        # Difficulty selector
        difficulty_frame = tk.Frame(top_frame)
        difficulty_frame.pack(pady=5)
        
        tk.Label(
            difficulty_frame,
            text="AI Difficulty:",
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        self.difficulty_var = tk.StringVar(value=self.difficulty)
        difficulty_menu = tk.OptionMenu(
            difficulty_frame,
            self.difficulty_var,
            *AIManager.get_difficulty_list(),
            command=self.change_difficulty
        )
        difficulty_menu.config(font=('Arial', 10), width=10)
        difficulty_menu.pack(side=tk.LEFT, padx=5)
        
        # Info label with difficulty description
        self.diff_info_label = tk.Label(
            top_frame,
            text=AIManager.get_description(self.difficulty),
            font=('Arial', 9, 'italic'),
            fg='gray'
        )
        self.diff_info_label.pack()
        
        self.status_label = tk.Label(
            top_frame,
            text="Your turn! (You are Black/X)",
            font=('Arial', 14, 'bold'),
            fg='darkgreen'
        )
        self.status_label.pack(pady=5)
        
        # Canvas for game board
        canvas_size = self.board_size * self.cell_size
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_size,
            height=canvas_size,
            bg='burlywood'
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind('<Button-1>', self.on_click)
        
        # Draw grid
        self.draw_board()
        
        # Bottom frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.new_game_button = tk.Button(
            button_frame,
            text="New Game",
            command=self.new_game,
            font=('Arial', 12),
            bg='lightblue',
            width=10
        )
        self.new_game_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(
            button_frame,
            text="Pause",
            command=self.pause_game,
            font=('Arial', 12),
            bg='lightyellow',
            width=10
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = tk.Button(
            button_frame,
            text="Save Game",
            command=self.save_game,
            font=('Arial', 12),
            bg='lightgreen',
            width=10
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.stats_button = tk.Button(
            button_frame,
            text="Statistics",
            command=self.show_statistics,
            font=('Arial', 12),
            bg='lightsteelblue',
            width=10
        )
        self.stats_button.pack(side=tk.LEFT, padx=5)
        
        self.quit_button = tk.Button(
            button_frame,
            text="Quit",
            command=self.quit_game,
            font=('Arial', 12),
            bg='lightcoral',
            width=10
        )
        self.quit_button.pack(side=tk.LEFT, padx=5)
        
    def draw_board(self):
        """Draw the game board grid"""
        for i in range(self.board_size + 1):
            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.board_size * self.cell_size, fill='black')
            
            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.board_size * self.cell_size, y, fill='black')
    
    def draw_stone(self, row, col, player):
        """Draw a stone on the board"""
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 3
        
        color = 'black' if player == 'X' else 'white'
        outline = 'white' if player == 'X' else 'black'
        
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color,
            outline=outline,
            width=2
        )
    
    def on_click(self, event):
        """Handle board click"""
        if not self.game_active:
            return
        
        # Convert click to board coordinates
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if not self.game.is_valid_move(row, col):
            return
        
        # Make player move
        self.game.make_move(row, col, self.player_symbol)
        self.draw_stone(row, col, self.player_symbol)
        
        # Check if player won
        if self.game.game_over:
            self.game_active = False
            self.update_status("You win! 🎉", 'green')
            self.statistics.record_game('singleplayer', 'win', self.difficulty)
            messagebox.showinfo("Game Over", "Congratulations! You won! 🎉")
            return
        
        # Check for draw (board full)
        if self.is_board_full():
            self.game_active = False
            self.update_status("Draw! Board is full", 'orange')
            self.statistics.record_game('singleplayer', 'draw', self.difficulty)
            messagebox.showinfo("Game Over", "It's a draw! The board is full.")
            return
        
        # AI's turn
        self.update_status("AI is thinking...", 'blue')
        self.root.update()
        self.root.after(500, self.ai_move)  # Delay for effect
    
    def ai_move(self):
        """Let AI make a move"""
        if not self.game_active:
            return
        
        move = self.ai.make_move()
        if move:
            row, col = move
            self.game.make_move(row, col, self.ai_symbol)
            self.draw_stone(row, col, self.ai_symbol)
            
            # Check if AI won
            if self.game.game_over:
                self.game_active = False
                self.update_status("AI wins! 😢", 'red')
                self.statistics.record_game('singleplayer', 'loss', self.difficulty)
                messagebox.showinfo("Game Over", "AI wins! Better luck next time!")
                return
            
            # Check for draw
            if self.is_board_full():
                self.game_active = False
                self.update_status("Draw! Board is full", 'orange')
                self.statistics.record_game('singleplayer', 'draw', self.difficulty)
                messagebox.showinfo("Game Over", "It's a draw! The board is full.")
                return
        
        # Player's turn again
        self.update_status("Your turn! (You are Black/X)", 'darkgreen')
    
    def is_board_full(self):
        """Check if the board is full"""
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                if self.game.board[row][col] == ' ':
                    return False
        return True
    
    def new_game(self):
        """Start a new game"""
        self.canvas.delete('all')
        self.draw_board()
        self.game.reset()
        self.game_active = True
        # Recreate AI with current difficulty
        self.ai = AIManager.get_ai(self.game, self.difficulty, self.ai_symbol)
        self.update_status("Your turn! (You are Black/X)", 'darkgreen')
    
    def change_difficulty(self, new_difficulty):
        """Change AI difficulty level"""
        self.difficulty = new_difficulty
        self.diff_info_label.config(text=AIManager.get_description(new_difficulty))
        
        # Ask if user wants to restart
        if self.game_active:
            response = messagebox.askyesno(
                "Difficulty Changed",
                f"AI difficulty changed to {new_difficulty}.\nStart a new game?",
                icon='question'
            )
            if response:
                self.new_game()
        else:
            # Just update AI for next game
            self.ai = AIManager.get_ai(self.game, self.difficulty, self.ai_symbol)
    
    def update_status(self, text, color='black'):
        """Update status label"""
        self.status_label.config(text=text, fg=color)
    
    def pause_game(self):
        """Pause the game and show pause menu"""
        if not self.game_active:
            messagebox.showinfo("Game Paused", "Game is already over!")
            return
        
        # Temporarily disable game
        was_active = self.game_active
        self.game_active = False
        self.update_status("Game Paused", 'orange')
        
        # Show pause dialog
        response = messagebox.askquestion(
            "Game Paused",
            "Game is paused.\n\nDo you want to:\n• Yes - Continue playing\n• No - Save and quit",
            icon='question'
        )
        
        if response == 'yes':
            # Continue playing
            self.game_active = was_active
            self.update_status("Your turn! (You are Black/X)", 'darkgreen')
        else:
            # Save and quit
            self.save_and_quit()
    
    def save_game(self):
        """Save current game state"""
        if GameStateManager.save_game(
            self.game,
            game_mode='singleplayer',
            ai_difficulty=self.difficulty
        ):
            messagebox.showinfo(
                "Game Saved",
                "Game has been saved successfully!\nYou can continue later."
            )
        else:
            messagebox.showerror(
                "Save Failed",
                "Failed to save game. Please try again."
            )
    
    def save_and_quit(self):
        """Save game and quit"""
        if GameStateManager.save_game(
            self.game,
            game_mode='singleplayer',
            ai_difficulty=self.difficulty
        ):
            messagebox.showinfo(
                "Game Saved",
                "Game saved successfully!\nSee you next time!"
            )
            self.root.quit()
            self.root.destroy()
        else:
            # Ask if user still wants to quit
            response = messagebox.askyesno(
                "Save Failed",
                "Failed to save game.\nQuit anyway?",
                icon='warning'
            )
            if response:
                self.root.quit()
                self.root.destroy()
    
    def load_game(self):
        """Load saved game state"""
        state = GameStateManager.load_game()
        
        if state is None:
            messagebox.showerror(
                "Load Failed",
                "No saved game found or failed to load."
            )
            return False
        
        try:
            # Restore game state
            self.game.board = state['board']
            self.game.board_size = state['board_size']
            self.game.current_player = state['current_player']
            self.game.game_over = state['game_over']
            self.game.winner = state['winner']
            
            # Restore AI difficulty
            self.difficulty = state['ai_difficulty']
            self.difficulty_var.set(self.difficulty)
            self.diff_info_label.config(text=AIManager.get_description(self.difficulty))
            self.ai = AIManager.get_ai(self.game, self.difficulty, self.ai_symbol)
            
            # Redraw board
            self.canvas.delete('all')
            self.draw_board()
            
            for row in range(self.game.board_size):
                for col in range(self.game.board_size):
                    player = self.game.board[row][col]
                    if player != ' ':
                        self.draw_stone(row, col, player)
            
            # Set game active
            self.game_active = not self.game.game_over
            
            if self.game.game_over:
                self.update_status(f"Game Over - Winner: {self.game.winner}", 'red')
            else:
                self.update_status("Game loaded! Your turn!", 'darkgreen')
            
            messagebox.showinfo(
                "Game Loaded",
                f"Game loaded successfully!\nDifficulty: {self.difficulty}"
            )
            return True
            
        except Exception as e:
            messagebox.showerror(
                "Load Error",
                f"Failed to restore game state: {e}"
            )
            return False
    
    def show_statistics(self):
        """Show game statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Game Statistics")
        stats_window.geometry("600x500")
        stats_window.resizable(False, False)
        
        # Title
        title_label = tk.Label(
            stats_window,
            text="Your Game Statistics",
            font=('Arial', 16, 'bold'),
            pady=10
        )
        title_label.pack()
        
        # Statistics text
        stats_text = scrolledtext.ScrolledText(
            stats_window,
            width=70,
            height=20,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        stats_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Insert statistics
        summary = self.statistics.get_statistics_summary()
        stats_text.insert(tk.END, summary)
        stats_text.config(state=tk.DISABLED)
        
        # Buttons frame
        button_frame = tk.Frame(stats_window)
        button_frame.pack(pady=10)
        
        # Reset button
        reset_button = tk.Button(
            button_frame,
            text="Reset Statistics",
            command=lambda: self.reset_statistics(stats_window),
            font=('Arial', 11),
            bg='orange',
            fg='white',
            width=15
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=stats_window.destroy,
            font=('Arial', 11),
            bg='lightblue',
            width=15
        )
        close_button.pack(side=tk.LEFT, padx=5)
    
    def reset_statistics(self, window):
        """Reset all statistics"""
        response = messagebox.askyesno(
            "Reset Statistics",
            "Are you sure you want to reset all statistics?\nThis cannot be undone!",
            icon='warning'
        )
        
        if response:
            self.statistics.reset_statistics()
            messagebox.showinfo("Statistics Reset", "All statistics have been reset!")
            window.destroy()
    
    def quit_game(self):
        """Quit the game"""
        if self.game_active:
            response = messagebox.askyesnocancel(
                "Quit Game",
                "Do you want to save before quitting?\n\n• Yes - Save and quit\n• No - Quit without saving\n• Cancel - Continue playing",
                icon='question'
            )
            
            if response is None:  # Cancel
                return
            elif response:  # Yes - save
                self.save_and_quit()
                return
            # No - just quit (fall through)
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the game"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.root.mainloop()


if __name__ == "__main__":
    game = GomokuSinglePlayer()
    game.run()
