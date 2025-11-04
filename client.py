"""
Gomoku Game Client with GUI
Connects to game server and provides graphical interface
"""

import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from game import GomokuGame


class GomokuClient:
    """Client with GUI for Gomoku game"""
    
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.player_symbol = None
        self.game_id = None
        self.my_turn = False
        self.connected = False
        
        # Game state
        self.board_size = 15
        self.game = GomokuGame(self.board_size)
        
        # GUI
        self.root = tk.Tk()
        self.root.title("Gomoku - Online Multiplayer")
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
            text="Click 'Connect' to start",
            font=('Arial', 14, 'bold')
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
        
        self.connect_button = tk.Button(
            button_frame,
            text="Connect to Server",
            command=self.connect_to_server,
            font=('Arial', 12),
            bg='lightgreen'
        )
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.new_game_button = tk.Button(
            button_frame,
            text="New Game",
            command=self.request_new_game,
            font=('Arial', 12),
            state=tk.DISABLED
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
            self.canvas.create_line(x, 0, x, self.board_size * self.cell_size)
            
            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.board_size * self.cell_size, y)
    
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
        if not self.connected or not self.my_turn:
            return
        
        # Convert click to board coordinates
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if not self.game.is_valid_move(row, col):
            return
        
        # Make move locally
        self.game.make_move(row, col, self.player_symbol)
        self.draw_stone(row, col, self.player_symbol)
        
        # Send move to server
        self.send_move(row, col)
        self.my_turn = False
        self.update_status("Opponent's turn...")
    
    def connect_to_server(self):
        """Connect to the game server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            self.connect_button.config(state=tk.DISABLED)
            self.update_status("Connected! Waiting for opponent...")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
    
    def receive_messages(self):
        """Receive messages from server"""
        try:
            while self.connected:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)
                
        except Exception as e:
            if self.connected:
                print(f"Error receiving message: {e}")
                self.root.after(0, lambda: messagebox.showerror("Connection Lost", "Lost connection to server"))
                self.connected = False
    
    def handle_message(self, message):
        """Handle different message types from server"""
        msg_type = message['type']
        
        if msg_type == 'waiting':
            self.player_symbol = message['player']
            self.game_id = message['game_id']
            self.root.after(0, lambda: self.update_status(message['message']))
            
        elif msg_type == 'start':
            self.player_symbol = message['player']
            self.game_id = message['game_id']
            self.my_turn = (self.player_symbol == 'X')
            
            status = f"You are {self.player_symbol}. " + ("Your turn!" if self.my_turn else "Opponent's turn")
            self.root.after(0, lambda: self.update_status(status))
            self.root.after(0, lambda: self.new_game_button.config(state=tk.NORMAL))
            
        elif msg_type == 'opponent_move':
            row, col = message['row'], message['col']
            player = message['player']
            
            self.game.make_move(row, col, player)
            self.root.after(0, lambda: self.draw_stone(row, col, player))
            
            if self.game.game_over:
                self.root.after(0, lambda: self.show_game_over(False))
            else:
                self.my_turn = True
                self.root.after(0, lambda: self.update_status("Your turn!"))
            
        elif msg_type == 'game_over':
            winner = message['winner']
            self.my_turn = False
            you_won = (winner == self.player_symbol)
            self.root.after(0, lambda: self.show_game_over(you_won))
            
        elif msg_type == 'reset':
            self.root.after(0, self.reset_board)
            
        elif msg_type == 'opponent_disconnected':
            self.root.after(0, lambda: messagebox.showinfo("Game Over", message['message']))
            self.root.after(0, self.quit_game)
            
        elif msg_type == 'error':
            self.root.after(0, lambda: messagebox.showerror("Error", message['message']))
    
    def send_move(self, row, col):
        """Send move to server"""
        try:
            message = {
                'type': 'move',
                'row': row,
                'col': col
            }
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send move: {e}")
    
    def request_new_game(self):
        """Request a new game"""
        self.reset_board()
        try:
            message = {'type': 'reset'}
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to request new game: {e}")
    
    def reset_board(self):
        """Reset the board for new game"""
        self.canvas.delete('all')
        self.draw_board()
        self.game.reset()
        self.my_turn = (self.player_symbol == 'X')
        status = f"New game! You are {self.player_symbol}. " + ("Your turn!" if self.my_turn else "Opponent's turn")
        self.update_status(status)
    
    def show_game_over(self, you_won):
        """Show game over message"""
        message = "You won! 🎉" if you_won else "You lost! 😢"
        self.update_status(f"Game Over! {message}")
        messagebox.showinfo("Game Over", message)
    
    def update_status(self, text):
        """Update status label"""
        self.status_label.config(text=text)
    
    def quit_game(self):
        """Quit the game"""
        if self.connected:
            try:
                message = {'type': 'disconnect'}
                data = json.dumps(message).encode('utf-8')
                self.socket.send(data)
                self.socket.close()
            except:
                pass
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the client"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.root.mainloop()


if __name__ == "__main__":
    # Get server address from user
    root = tk.Tk()
    root.withdraw()
    
    host = simpledialog.askstring(
        "Server Address",
        "Enter server IP address (leave empty for localhost):",
        initialvalue="127.0.0.1"
    )
    
    if host is None:
        exit()
    
    if not host:
        host = "127.0.0.1"
    
    root.destroy()
    
    # Start client
    client = GomokuClient(host=host, port=5555)
    client.run()
