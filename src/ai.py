import random

class GomokuAI:
    """Simple random AI opponent"""
    
    def __init__(self, game):
        self.game = game
    
    def make_move(self):
        """Make a random valid move"""
        valid_moves = []
        
        # Find all valid moves
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                if self.game.is_valid_move(row, col):
                    valid_moves.append((row, col))
        
        # Choose random move
        if valid_moves:
            return random.choice(valid_moves)
        return None