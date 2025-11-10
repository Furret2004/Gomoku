"""
Minimax AI with Alpha-Beta Pruning for Gomoku
Implements strategic gameplay using search algorithms
"""

import copy
from typing import Tuple, List, Optional


class MinimaxAI:
    """
    Minimax AI with alpha-beta pruning for Gomoku
    Evaluates board positions using pattern-based heuristics
    """
    
    # Scoring constants for pattern evaluation
    FIVE = 100000       # Five in a row (win)
    OPEN_FOUR = 10000   # Four in a row with both ends open
    BLOCKED_FOUR = 5000 # Four in a row with one end blocked
    OPEN_THREE = 1000   # Three in a row with both ends open
    BLOCKED_THREE = 100 # Three in a row with one end blocked
    OPEN_TWO = 10       # Two in a row with both ends open
    BLOCKED_TWO = 1     # Two in a row with one end blocked
    
    def __init__(self, game, player='O', depth=3, use_alpha_beta=True):
        """
        Initialize Minimax AI
        
        Args:
            game: GomokuGame instance
            player: AI player symbol ('O' or 'X')
            depth: Search depth (2-4 recommended)
            use_alpha_beta: Enable alpha-beta pruning
        """
        self.game = game
        self.player = player
        self.opponent = 'X' if player == 'O' else 'O'
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.nodes_evaluated = 0  # For performance tracking
        
    def make_move(self) -> Optional[Tuple[int, int]]:
        """
        Find and return the best move using minimax algorithm
        
        Returns:
            (row, col) tuple or None if no valid moves
        """
        self.nodes_evaluated = 0
        best_move = self.get_best_move()
        print(f"[AI] Evaluated {self.nodes_evaluated} nodes, depth={self.depth}")
        return best_move
    
    def get_best_move(self) -> Optional[Tuple[int, int]]:
        """
        Get best move using minimax with alpha-beta pruning
        
        Returns:
            Best (row, col) move or None
        """
        legal_moves = self.get_legal_moves_nearby()
        
        if not legal_moves:
            return None
        
        # Quick win check - if we can win in one move, take it
        for move in legal_moves:
            if self.is_winning_move(move, self.player):
                return move
        
        # Quick block check - if opponent can win, block it
        for move in legal_moves:
            if self.is_winning_move(move, self.opponent):
                return move
        
        # Order moves by proximity to existing stones
        ordered_moves = self.order_moves(legal_moves)
        
        best_score = float('-inf')
        best_move = ordered_moves[0]  # Default to first move
        alpha = float('-inf')
        beta = float('inf')
        
        for move in ordered_moves:
            row, col = move
            
            # Try this move
            original_value = self.game.board[row][col]
            self.game.board[row][col] = self.player
            
            # Evaluate with minimax
            if self.use_alpha_beta:
                score = self.minimax(self.depth - 1, alpha, beta, False)
            else:
                score = self.minimax(self.depth - 1, alpha, beta, False)
            
            # Undo move
            self.game.board[row][col] = original_value
            
            # Update best move
            if score > best_score:
                best_score = score
                best_move = move
            
            # Update alpha for pruning
            alpha = max(alpha, best_score)
        
        return best_move
    
    def minimax(self, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning
        
        Args:
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player's turn
            
        Returns:
            Evaluation score
        """
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if depth == 0:
            return self.evaluate_board()
        
        # Check if game is over
        if self.is_game_over():
            winner = self.get_winner()
            if winner == self.player:
                return self.FIVE
            elif winner == self.opponent:
                return -self.FIVE
            else:
                return 0  # Draw
        
        legal_moves = self.get_legal_moves_nearby()
        if not legal_moves:
            return 0  # Draw
        
        # Order moves for better pruning
        ordered_moves = self.order_moves(legal_moves)
        
        if maximizing:
            max_eval = float('-inf')
            for move in ordered_moves:
                row, col = move
                
                # Make move
                original_value = self.game.board[row][col]
                self.game.board[row][col] = self.player
                
                # Recurse
                eval_score = self.minimax(depth - 1, alpha, beta, False)
                
                # Undo move
                self.game.board[row][col] = original_value
                
                max_eval = max(max_eval, eval_score)
                
                # Alpha-beta pruning
                if self.use_alpha_beta:
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break  # Beta cutoff
                
            return max_eval
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                row, col = move
                
                # Make move
                original_value = self.game.board[row][col]
                self.game.board[row][col] = self.opponent
                
                # Recurse
                eval_score = self.minimax(depth - 1, alpha, beta, True)
                
                # Undo move
                self.game.board[row][col] = original_value
                
                min_eval = min(min_eval, eval_score)
                
                # Alpha-beta pruning
                if self.use_alpha_beta:
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha cutoff
                
            return min_eval
    
    def evaluate_board(self) -> float:
        """
        Evaluate current board position using pattern-based heuristics
        
        Returns:
            Score (positive = good for AI, negative = good for opponent)
        """
        ai_score = self.evaluate_player(self.player)
        opp_score = self.evaluate_player(self.opponent)
        
        return ai_score - opp_score
    
    def evaluate_player(self, player: str) -> float:
        """
        Evaluate board for a specific player by counting patterns
        
        Args:
            player: Player symbol to evaluate
            
        Returns:
            Total score for this player
        """
        score = 0
        board = self.game.board
        size = self.game.board_size
        
        # Check all directions: horizontal, vertical, diagonal \, diagonal /
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal \
            (1, -1)   # Diagonal /
        ]
        
        checked = set()  # Avoid double counting
        
        for row in range(size):
            for col in range(size):
                if board[row][col] != player:
                    continue
                
                for dr, dc in directions:
                    # Create unique key for this line
                    key = (row, col, dr, dc)
                    if key in checked:
                        continue
                    
                    # Count consecutive stones in this direction
                    length = 0
                    r, c = row, col
                    
                    while (0 <= r < size and 0 <= c < size and 
                           board[r][c] == player):
                        length += 1
                        checked.add((r, c, dr, dc))
                        r += dr
                        c += dc
                    
                    # Check if line is blocked on ends
                    # Check start
                    start_r = row - dr
                    start_c = col - dc
                    start_blocked = (not (0 <= start_r < size and 0 <= start_c < size) or
                                   board[start_r][start_c] != ' ')
                    
                    # Check end
                    end_r = row + dr * length
                    end_c = col + dc * length
                    end_blocked = (not (0 <= end_r < size and 0 <= end_c < size) or
                                 board[end_r][end_c] != ' ')
                    
                    # Score based on pattern
                    if length >= 5:
                        score += self.FIVE
                    elif length == 4:
                        if not start_blocked and not end_blocked:
                            score += self.OPEN_FOUR
                        else:
                            score += self.BLOCKED_FOUR
                    elif length == 3:
                        if not start_blocked and not end_blocked:
                            score += self.OPEN_THREE
                        else:
                            score += self.BLOCKED_THREE
                    elif length == 2:
                        if not start_blocked and not end_blocked:
                            score += self.OPEN_TWO
                        else:
                            score += self.BLOCKED_TWO
        
        return score
    
    def get_legal_moves_nearby(self, radius=2):
        moves = set()
        board = self.game.board
        size = self.game.board_size
        
        # If board empty, return center
        if all(board[r][c] == ' ' for r in range(size) for c in range(size)):
            return [(size // 2, size // 2)]
        
        # Find all occupied positions
        for row in range(size):
            for col in range(size):
                if board[row][col] != ' ':
                    # Add all empty cells within radius
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            r, c = row + dr, col + dc
                            if (0 <= r < size and 0 <= c < size and 
                                board[r][c] == ' '):
                                moves.add((r, c))
        
        return list(moves)
    
    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """
        Get all legal moves on the board
        
        Returns:
            List of (row, col) tuples
        """
        moves = []
        size = self.game.board_size
        
        for row in range(size):
            for col in range(size):
                if self.game.board[row][col] == ' ':
                    moves.append((row, col))
        
        return moves
    
    def order_moves(self, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Order moves by proximity to existing stones
        Moves near existing stones are more likely to be good
        
        Args:
            moves: List of (row, col) moves
            
        Returns:
            Ordered list of moves
        """
        if not moves:
            return moves
        
        # If board is empty, return center
        if all(self.game.board[r][c] == ' ' 
               for r in range(self.game.board_size) 
               for c in range(self.game.board_size)):
            center = self.game.board_size // 2
            return [(center, center)]
        
        # Score each move by proximity to existing stones
        scored_moves = []
        
        for move in moves:
            row, col = move
            min_distance = float('inf')
            
            # Find distance to nearest stone
            for r in range(self.game.board_size):
                for c in range(self.game.board_size):
                    if self.game.board[r][c] != ' ':
                        distance = abs(row - r) + abs(col - c)
                        min_distance = min(min_distance, distance)
            
            scored_moves.append((min_distance, move))
        
        # Sort by distance (closer is better)
        scored_moves.sort(key=lambda x: x[0])
        
        return [move for _, move in scored_moves]
    
    def is_winning_move(self, move: Tuple[int, int], player: str) -> bool:
        """
        Check if a move results in immediate win
        
        Args:
            move: (row, col) position
            player: Player symbol
            
        Returns:
            True if move wins the game
        """
        row, col = move
        
        # Temporarily make the move
        original = self.game.board[row][col]
        self.game.board[row][col] = player
        
        # Check if it's a winning position
        is_win = self.game.check_winner(row, col, player)
        
        # Undo move
        self.game.board[row][col] = original
        
        return is_win
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.game.game_over or not self.get_legal_moves()
    
    def get_winner(self) -> Optional[str]:
        """Get winner if game is over"""
        return self.game.winner if self.game.game_over else None
