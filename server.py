"""
Gomoku Game Server
Handles multiple clients and game rooms
"""

import socket
import threading
import json
from game import GomokuGame


class GameServer:
    """Server to handle multiple game rooms"""
    
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.games = {}  # game_id -> game instance
        self.waiting_player = None  # Player waiting for opponent
        self.game_counter = 0
        
    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"[SERVER] Started on {self.host}:{self.port}")
        print("[SERVER] Waiting for connections...")
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"[SERVER] New connection from {address}")
                
                # Create thread for each client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        game_id = None
        player_symbol = None
        opponent_socket = None
        
        try:
            # Match players
            if self.waiting_player is None:
                # First player - wait for opponent
                self.waiting_player = {
                    'socket': client_socket,
                    'address': address
                }
                player_symbol = 'X'
                
                # Create new game
                game_id = self.game_counter
                self.game_counter += 1
                self.games[game_id] = {
                    'game': GomokuGame(),
                    'player_X': client_socket,
                    'player_O': None
                }
                
                self.send_message(client_socket, {
                    'type': 'waiting',
                    'player': player_symbol,
                    'game_id': game_id,
                    'message': 'Waiting for opponent...'
                })
                
                print(f"[SERVER] Player X waiting in game {game_id}")
                
                # Wait for opponent (blocking)
                while self.games[game_id]['player_O'] is None:
                    threading.Event().wait(0.1)
                
                opponent_socket = self.games[game_id]['player_O']
                
            else:
                # Second player - start game
                player_symbol = 'O'
                game_id = self.waiting_player['game_id'] if 'game_id' in self.waiting_player else self.game_counter - 1
                
                self.games[game_id]['player_O'] = client_socket
                opponent_socket = self.games[game_id]['player_X']
                
                # Notify both players
                self.send_message(client_socket, {
                    'type': 'start',
                    'player': player_symbol,
                    'game_id': game_id,
                    'message': 'Game starting! You are O'
                })
                
                self.send_message(opponent_socket, {
                    'type': 'start',
                    'player': 'X',
                    'game_id': game_id,
                    'message': 'Game starting! You are X (you go first)'
                })
                
                print(f"[SERVER] Game {game_id} started!")
                self.waiting_player = None
            
            # Game loop
            game = self.games[game_id]['game']
            
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                
                if message['type'] == 'move':
                    row, col = message['row'], message['col']
                    
                    # Validate move
                    if game.make_move(row, col, player_symbol):
                        # Send move to opponent
                        self.send_message(opponent_socket, {
                            'type': 'opponent_move',
                            'row': row,
                            'col': col,
                            'player': player_symbol
                        })
                        
                        # Check if game over
                        if game.game_over:
                            self.send_message(client_socket, {
                                'type': 'game_over',
                                'winner': game.winner,
                                'message': 'You win!'
                            })
                            self.send_message(opponent_socket, {
                                'type': 'game_over',
                                'winner': game.winner,
                                'message': 'You lose!'
                            })
                            break
                    else:
                        self.send_message(client_socket, {
                            'type': 'error',
                            'message': 'Invalid move'
                        })
                
                elif message['type'] == 'reset':
                    game.reset()
                    self.send_message(opponent_socket, {
                        'type': 'reset',
                        'message': 'Opponent requested new game'
                    })
                
                elif message['type'] == 'disconnect':
                    break
                    
        except Exception as e:
            print(f"[SERVER] Error with {address}: {e}")
        
        finally:
            # Clean up
            if game_id is not None and game_id in self.games:
                # Notify opponent
                if opponent_socket:
                    try:
                        self.send_message(opponent_socket, {
                            'type': 'opponent_disconnected',
                            'message': 'Opponent disconnected'
                        })
                    except:
                        pass
                
                # Remove game
                del self.games[game_id]
            
            if self.waiting_player and self.waiting_player['socket'] == client_socket:
                self.waiting_player = None
            
            client_socket.close()
            print(f"[SERVER] Connection closed: {address}")
    
    def send_message(self, client_socket, message):
        """Send JSON message to client"""
        try:
            data = json.dumps(message).encode('utf-8')
            client_socket.send(data)
        except Exception as e:
            print(f"[SERVER] Error sending message: {e}")


if __name__ == "__main__":
    server = GameServer()
    server.start()
