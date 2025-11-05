import tkinter as tk
from tkinter import messagebox
from src.game import GomokuGame
from src.ai import GomokuAI, MinimaxAI

class GomokuSinglePlayer:
    """Single player Gomoku game with GUI"""
    
    def __init__(self):
        self.board_size = 15
        self.game = GomokuGame(self.board_size)
        self.ai = None 
        
        self.player_symbol = 'X'
        self.ai_symbol = 'O'
        self.game_active = False 
        
        self.root = tk.Tk()
        self.root.title("Gomoku - Single Player vs AI")
        self.root.resizable(False, False)
        self.root.configure(bg='lightgray')
        
        self.cell_size = 40

        self.create_difficulty()
        
    def create_difficulty(self):
        self.selection_frame = tk.Frame(self.root, padx=20, pady=40, bg='lightgray')
        self.selection_frame.pack()
        
        title_label = tk.Label(
            self.selection_frame,
            text="Choose AI Difficulty",
            font=('Arial', 20, 'bold'),
            bg='lightgray'
        )
        title_label.pack(pady=20)
        
        easy_button = tk.Button(
            self.selection_frame,
            text="Easy (Random AI)",
            font=('Arial', 14),
            width=20,
            command=lambda: self.start_game('easy')
        )
        easy_button.pack(pady=10)
        
        hard_button = tk.Button(
            self.selection_frame,
            text="Hard (Minimax AI)",
            font=('Arial', 14),
            width=20,
            command=lambda: self.start_game('hard')
        )
        hard_button.pack(pady=10)

    def start_game(self, difficulty):
        self.selection_frame.destroy()

        if difficulty == 'easy':
            self.ai = GomokuAI(self.game)
        elif difficulty == 'hard':
            self.ai = MinimaxAI(self.game, self.ai_symbol, self.player_symbol, depth=2) 

        self.game_active = True
        self.create_gui() 

    def create_gui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            top_frame,
            text="Your turn! (You are Black/X)",
            font=('Arial', 14, 'bold'),
            fg='darkgreen'
        )
        self.status_label.pack()
        
        canvas_size = self.board_size * self.cell_size
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_size,
            height=canvas_size,
            bg='burlywood'
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind('<Button-1>', self.on_click)
        
        self.draw_board()
        
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
        for i in range(self.board_size + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.board_size * self.cell_size, fill='black')
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.board_size * self.cell_size, y, fill='black')
    
    def draw_stone(self, row, col, player):
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 3
        color = 'black' if player == 'X' else 'white'
        outline = 'white' if player == 'X' else 'black'
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline=outline, width=2
        )
    
    def on_click(self, event):
        if not self.game_active:
            return
        
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if not self.game.is_valid_move(row, col):
            return
        
        self.game.make_move(row, col, self.player_symbol)
        self.draw_stone(row, col, self.player_symbol)
        
        if self.game.game_over:
            self.game_active = False
            self.update_status("You win! 🎉", 'green')
            messagebox.showinfo("Game Over", "Congratulations! You won! 🎉")
            return
        
        if self.game.is_board_full():
            self.game_active = False
            self.update_status("Draw! Board is full", 'orange')
            messagebox.showinfo("Game Over", "It's a draw! The board is full.")
            return
        
        self.update_status("AI is thinking...", 'blue')
        self.root.update()
        self.root.after(100, self.ai_move) 
    
    def ai_move(self):
        if not self.game_active:
            return
        
        move = self.ai.getBestMove()
        if move:
            row, col = move
            self.game.make_move(row, col, self.ai_symbol)
            self.draw_stone(row, col, self.ai_symbol)
            
            if self.game.game_over:
                self.game_active = False
                self.update_status("AI wins! 😢", 'red')
                messagebox.showinfo("Game Over", "AI wins! Better luck next time!")
                return
            
            if self.game.is_board_full():
                self.game_active = False
                self.update_status("Draw! Board is full", 'orange')
                messagebox.showinfo("Game Over", "It's a draw! The board is full.")
                return
        
        self.update_status("Your turn! (You are Black/X)", 'darkgreen')
    
    def new_game(self):
        self.canvas.delete('all')
        self.draw_board()
        self.game.reset()
        self.game_active = True
        self.update_status("Your turn! (You are Black/X)", 'darkgreen')
    
    def update_status(self, text, color='black'):
        self.status_label.config(text=text, fg=color)
    
    def quit_game(self):
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.root.mainloop()

if __name__ == "__main__":
    game = GomokuSinglePlayer()
    game.run()