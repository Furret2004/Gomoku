"""
Gomoku Single Player vs AI
Play against a computer opponent with GUI
"""

import tkinter as tk
from tkinter import messagebox
from src.game import GomokuGame
from src.ai import GomokuAI


class GomokuSinglePlayer:
    """Single player Gomoku game with GUI"""
    
    def __init__(self):
        self.board_size = 15
        self.game = GomokuGame(self.board_size)
        self.ai = GomokuAI(self.game)
        
        self.player_symbol = 'X'  # Player is X (black)
        self.ai_symbol = 'O'      # AI is O (white)
        self.game_active = True
        
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
        
        self.status_label = tk.Label(
            top_frame,
            text="Your turn! (You are Black/X)",
            font=('Arial', 14, 'bold'),
            fg='darkgreen'
        )
        self.status_label.pack()
        
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
            bg='lightblue'
        )
        self.new_game_button.pack(side=tk.LEFT, padx=5)
        
        self.quit_button = tk.Button(
            button_frame,
            text="Quit",
            command=self.quit_game,
            font=('Arial', 12),
            bg='lightcoral'
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
            messagebox.showinfo("Game Over", "Congratulations! You won! 🎉")
            return
        
        # Check for draw (board full)
        if self.is_board_full():
            self.game_active = False
            self.update_status("Draw! Board is full", 'orange')
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
                messagebox.showinfo("Game Over", "AI wins! Better luck next time!")
                return
            
            # Check for draw
            if self.is_board_full():
                self.game_active = False
                self.update_status("Draw! Board is full", 'orange')
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
        self.update_status("Your turn! (You are Black/X)", 'darkgreen')
    
    def update_status(self, text, color='black'):
        """Update status label"""
        self.status_label.config(text=text, fg=color)
    
    def quit_game(self):
        """Quit the game"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the game"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.root.mainloop()


if __name__ == "__main__":
    game = GomokuSinglePlayer()
    game.run()
