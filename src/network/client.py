"""
Gomoku Game Client with GUI
Connects to game server and provides graphical interface
"""

import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
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
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        
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
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)  # Remove timeout after connection
            self.connected = True
            
            self.connect_button.config(state=tk.DISABLED)
            self.update_status("Connected! Waiting for opponent...")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except socket.timeout:
            messagebox.showerror(
                "Connection Timeout",
                f"Could not connect to server at {self.host}:{self.port}\nConnection timed out after 10 seconds."
            )
        except ConnectionRefusedError:
            messagebox.showerror(
                "Connection Refused",
                f"Server at {self.host}:{self.port} refused connection.\nMake sure the server is running."
            )
        except socket.gaierror:
            messagebox.showerror(
                "Invalid Address",
                f"Could not resolve host: {self.host}\nPlease check the IP address."
            )
        except Exception as e:
            messagebox.showerror(
                "Connection Error",
                f"Could not connect to server: {type(e).__name__}\n{e}"
            )
    
    def receive_messages(self):
        """Receive messages from server"""
        try:
            while self.connected:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.handle_message(message)
                except json.JSONDecodeError as je:
                    print(f"[Client] Invalid JSON received: {je}")
                    continue
                
        except ConnectionResetError:
            if self.connected:
                print("[Client] Server closed connection")
                self.connected = False
                self.root.after(0, self.handle_disconnection)
        except socket.error as se:
            if self.connected:
                print(f"[Client] Socket error: {se}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Network Error",
                    f"Network error occurred: {se}"
                ))
                self.connected = False
        except Exception as e:
            if self.connected:
                print(f"[Client] Error receiving message: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Connection Lost",
                    f"Lost connection to server: {type(e).__name__}"
                ))
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
            
            # Don't check game_over here - let the server's game_over message handle it
            # This prevents duplicate "You lose!" messages
            if not self.game.game_over:
                self.my_turn = True
                self.root.after(0, lambda: self.update_status("Your turn!"))
            
        elif msg_type == 'game_over':
            winner = message['winner']
            self.my_turn = False
            you_won = (winner == self.player_symbol)
            self.root.after(0, lambda: self.show_game_over(you_won))
            
        elif msg_type == 'reset':
            self.root.after(0, self.reset_board)
            
        elif msg_type == 'waiting_for_opponent':
            msg = message.get('message', 'Waiting for opponent...')
            self.root.after(0, lambda: self.update_status(msg))
            
        elif msg_type == 'opponent_disconnected':
            self.root.after(0, lambda: messagebox.showinfo("Game Over", message['message']))
            self.root.after(0, self.quit_game)
            
        elif msg_type == 'error':
            self.root.after(0, lambda: messagebox.showerror("Error", message['message']))
    
    def send_move(self, row, col):
        """Send move to server"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to server")
            return
        
        try:
            message = {
                'type': 'move',
                'row': row,
                'col': col
            }
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except socket.error as se:
            messagebox.showerror("Network Error", f"Failed to send move: {se}")
            self.connected = False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send move: {type(e).__name__}\n{e}")
    
    def request_new_game(self):
        """Request a new game"""
        # Disable button to prevent multiple clicks
        self.new_game_button.config(state=tk.DISABLED)
        try:
            message = {'type': 'reset'}
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
            self.update_status("Waiting for opponent to click New Game...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to request new game: {e}")
            self.new_game_button.config(state=tk.NORMAL)
    
    def reset_board(self):
        """Reset the board for new game"""
        self.canvas.delete('all')
        self.draw_board()
        self.game.reset()
        self.my_turn = (self.player_symbol == 'X')
        status = f"New game! You are {self.player_symbol}. " + ("Your turn!" if self.my_turn else "Opponent's turn")
        self.update_status(status)
        # Re-enable new game button
        self.new_game_button.config(state=tk.NORMAL)
    
    def show_game_over(self, you_won):
        """Show game over message"""
        message = "You won! 🎉" if you_won else "You lost! 😢"
        self.update_status(f"Game Over! {message}")
        messagebox.showinfo("Game Over", message)
    
    def update_status(self, text):
        """Update status label"""
        self.status_label.config(text=text)
    
    def handle_disconnection(self):
        """Handle disconnection with reconnection option"""
        response = messagebox.askyesno(
            "Connection Lost",
            f"Lost connection to server.\n\nAttempt to reconnect?\n(Attempts left: {self.max_reconnect_attempts - self.reconnect_attempts})",
            icon='warning'
        )
        
        if response and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            self.attempt_reconnect()
        else:
            messagebox.showinfo("Disconnected", "You have been disconnected from the server.")
            self.quit_game()
    
    def attempt_reconnect(self):
        """Try to reconnect to server"""
        self.update_status(f"Reconnecting... (Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        try:
            # Close old socket
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            
            # Try to reconnect
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)
            self.connected = True
            self.reconnect_attempts = 0
            
            self.update_status("Reconnected! Waiting for opponent...")
            messagebox.showinfo("Reconnected", "Successfully reconnected to server!")
            
            # Restart receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except Exception as e:
            print(f"[Client] Reconnection failed: {e}")
            if self.reconnect_attempts < self.max_reconnect_attempts:
                # Try again
                self.root.after(2000, lambda: self.handle_disconnection())
            else:
                messagebox.showerror(
                    "Reconnection Failed",
                    f"Could not reconnect after {self.max_reconnect_attempts} attempts."
                )
                self.quit_game()
    
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
