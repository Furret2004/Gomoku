"""
Gomoku Game Logic Module
Handles game board, moves, and win detection
"""


class GomokuGame:
    """Gomoku (Five in a Row) game logic"""
    
    def __init__(self, board_size=15):
        self.board_size = board_size
        self.board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 'X'  # X starts first
        self.winner = None
        self.game_over = False
        
    def make_move(self, row, col, player):
        """
        Make a move on the board
        Returns True if move is valid, False otherwise
        """
        if not self.is_valid_move(row, col):
            return False
            
        self.board[row][col] = player
        
        # Check for winner
        if self.check_winner(row, col, player):
            self.winner = player
            self.game_over = True
            
        return True
    
    def is_valid_move(self, row, col):
        """Check if a move is valid"""
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False
        return self.board[row][col] == ' '
    
    def check_winner(self, row, col, player):
        """Check if the last move resulted in a win"""
        directions = [
            [(0, 1), (0, -1)],   # Horizontal
            [(1, 0), (-1, 0)],   # Vertical
            [(1, 1), (-1, -1)],  # Diagonal \
            [(1, -1), (-1, 1)]   # Diagonal /
        ]
        
        for direction_pair in directions:
            count = 1  # Count the piece just placed
            
            # Check both directions
            for dr, dc in direction_pair:
                r, c = row + dr, col + dc
                while (0 <= r < self.board_size and 
                       0 <= c < self.board_size and 
                       self.board[r][c] == player):
                    count += 1
                    r += dr
                    c += dc
            
            if count >= 5:
                return True
        
        return False
    
    def get_board_state(self):
        """Get current board state as a string"""
        return '\n'.join([''.join(row) for row in self.board])
    
    def reset(self):
        """Reset the game"""
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
