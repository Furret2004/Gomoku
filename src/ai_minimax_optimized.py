"""
Optimized Minimax AI with Advanced Features
Week 1 Optimizations:
- Iterative Deepening with time limit
- Transposition Table with Zobrist hashing
- Advanced Move Ordering (win/block/threat/proximity)
- Threat Space Search (radius-based)
- Opening Book
"""

import copy
import time
import random
from typing import Tuple, List, Optional, Dict
from collections import defaultdict


class OpeningBook:
    """
    Opening book with common Gomoku openings
    """
    
    # Famous Gomoku openings (Renju style)
    OPENINGS = {
        'tenju': [  # 天守 - Straight Four
            (7, 7),   # Center
            (7, 8),   # Right
            (8, 7),   # Down
            (6, 7),   # Up
        ],
        'kanzuki': [  # 寒月 - Slant Opening
            (7, 7),
            (8, 8),
            (6, 6),
            (9, 9),
        ],
        'zangetsu': [  # 残月 - Remaining Moon
            (7, 7),
            (7, 6),
            (8, 8),
            (6, 6),
        ],
        'suigetsu': [  # 水月 - Moon Reflection
            (7, 7),
            (8, 7),
            (7, 8),
            (8, 8),
        ],
    }
    
    def __init__(self):
        self.current_opening = None
        self.move_count = 0
        
    def count_moves_on_board(self, board):
        """Count total moves on board"""
        count = 0
        for row in board:
            for cell in row:
                if cell != ' ':
                    count += 1
        return count
        
    def get_opening_move(self, board, move_number=None):
        """
        Get opening book move if available
        
        Args:
            board: Current board state
            move_number: Number of moves played (auto-detect if None)
            
        Returns:
            (row, col) move or None
        """
        # Auto-detect move count from board
        if move_number is None:
            move_number = self.count_moves_on_board(board)
        
        # Only use opening book for first 8 moves
        if move_number >= 8:
            return None
        
        # If this is first move, randomly choose opening
        if move_number == 0:
            self.current_opening = random.choice(list(self.OPENINGS.keys()))
            opening_moves = self.OPENINGS[self.current_opening]
            print(f"[AI] 📖 Selected opening: {self.current_opening}")
            return opening_moves[0]
        
        # Continue current opening if moves match
        if self.current_opening:
            opening_moves = self.OPENINGS[self.current_opening]
            
            # Verify board matches opening so far
            if self.matches_opening(board, opening_moves[:move_number]):
                if move_number < len(opening_moves):
                    print(f"[AI] 📖 Opening book continues: move {move_number + 1}")
                    return opening_moves[move_number]
        
        return None
    
    def matches_opening(self, board, moves):
        """Check if board matches opening sequence"""
        for row, col in moves:
            if board[row][col] == ' ':
                return False
        return True


class TranspositionTable:
    """
    Transposition table with Zobrist hashing
    Stores previously evaluated positions
    """
    
    def __init__(self, size=15):
        self.table = {}
        self.size = size
        self.current_hash = 0
        
        # Initialize Zobrist hash values with better randomness
        import hashlib
        seed = int(hashlib.md5(b"gomoku_zobrist_2025").hexdigest()[:16], 16)
        random.seed(seed)
        self.zobrist = {}
        
        # Generate random values for each position and player
        for row in range(size):
            for col in range(size):
                self.zobrist[(row, col, 'X')] = random.getrandbits(64)
                self.zobrist[(row, col, 'O')] = random.getrandbits(64)
    
    def hash_board(self, board):
        """
        Generate Zobrist hash for board state
        Much faster than tuple hashing
        """
        h = 0
        for row in range(self.size):
            for col in range(self.size):
                piece = board[row][col]
                if piece != ' ':
                    h ^= self.zobrist[(row, col, piece)]
        return h
    
    def update_hash(self, current_hash, row, col, piece):
        """
        Incrementally update hash when placing a piece
        Much faster than rehashing entire board
        """
        return current_hash ^ self.zobrist[(row, col, piece)]
    
    def store(self, board, depth, score, flag, best_move=None):
        """
        Store position evaluation
        
        Args:
            board: Board state
            depth: Depth of evaluation
            score: Evaluation score
            flag: 'exact', 'lower', or 'upper'
            best_move: Best move found (optional)
        """
        key = self.hash_board(board)
        self.table[key] = {
            'depth': depth,
            'score': score,
            'flag': flag,
            'best_move': best_move
        }
    
    def lookup(self, board, depth, alpha, beta):
        """
        Lookup position in table
        
        Returns:
            (score, move) if usable hit, else (None, None)
        """
        key = self.hash_board(board)
        
        if key not in self.table:
            return None, None
        
        entry = self.table[key]
        
        # Only use if depth is sufficient
        if entry['depth'] < depth:
            return None, entry.get('best_move')
        
        score = entry['score']
        flag = entry['flag']
        
        # Check if score is usable
        if flag == 'exact':
            return score, entry.get('best_move')
        elif flag == 'lower':
            if score >= beta:
                return score, entry.get('best_move')
        elif flag == 'upper':
            if score <= alpha:
                return score, entry.get('best_move')
        
        return None, entry.get('best_move')
    
    def clear(self):
        """Clear the table"""
        self.table.clear()
    
    def size_mb(self):
        """Get table size in MB"""
        import sys
        return sys.getsizeof(self.table) / (1024 * 1024)


class MinimaxAI:
    """
    Optimized Minimax AI with:
    - Iterative Deepening
    - Transposition Table
    - Advanced Move Ordering
    - Threat Space Search
    - Opening Book
    """
    
    # Scoring constants for pattern evaluation
    FIVE = 100000       # Five in a row (win)
    OPEN_FOUR = 10000   # Four in a row with both ends open
    BLOCKED_FOUR = 5000 # Four in a row with one end blocked
    OPEN_THREE = 1000   # Three in a row with both ends open
    BLOCKED_THREE = 100 # Three in a row with one end blocked
    OPEN_TWO = 10       # Two in a row with both ends open
    BLOCKED_TWO = 1     # Two in a row with one end blocked
    
    def __init__(self, game, player='O', depth=3, time_limit=5.0, 
                 use_opening_book=True, use_iterative_deepening=True):
        """
        Initialize Optimized Minimax AI
        
        Args:
            game: GomokuGame instance
            player: AI player symbol ('O' or 'X')
            depth: Maximum search depth
            time_limit: Time limit for move search (seconds)
            use_opening_book: Enable opening book
            use_iterative_deepening: Enable iterative deepening
        """
        self.game = game
        self.player = player
        self.opponent = 'X' if player == 'O' else 'O'
        self.max_depth = depth
        self.time_limit = time_limit
        self.use_opening_book = use_opening_book
        self.use_iterative_deepening = use_iterative_deepening
        
        # Performance tracking
        self.nodes_evaluated = 0
        self.transposition_hits = 0
        self.transposition_cutoffs = 0
        
        # Components
        self.transposition_table = TranspositionTable(game.board_size)
        self.opening_book = OpeningBook() if use_opening_book else None
        
    def make_move(self) -> Optional[Tuple[int, int]]:
        """
        Find and return the best move
        
        Returns:
            (row, col) tuple or None if no valid moves
        """
        start_time = time.time()
        
        # Try opening book first
        if self.use_opening_book and self.opening_book:
            opening_move = self.opening_book.get_opening_move(
                self.game.board
            )
            if opening_move and self.game.is_valid_move(*opening_move):
                print(f"[AI] 📚 Opening book move: {opening_move}")
                return opening_move
        
        # Reset counters
        self.nodes_evaluated = 0
        self.transposition_hits = 0
        self.transposition_cutoffs = 0
        
        # Get best move (with iterative deepening or fixed depth)
        if self.use_iterative_deepening:
            best_move = self.iterative_deepening_search(start_time)
        else:
            best_move = self.get_best_move()
        
        elapsed = time.time() - start_time
        
        # Statistics
        print(f"[AI] ⚡ Search completed in {elapsed:.2f}s")
        print(f"[AI] 📊 Nodes: {self.nodes_evaluated:,}, "
              f"TT hits: {self.transposition_hits:,}, "
              f"TT cutoffs: {self.transposition_cutoffs:,}")
        print(f"[AI] 💾 TT size: {self.transposition_table.size_mb():.2f} MB")
        
        return best_move
    
    def iterative_deepening_search(self, start_time):
        """
        Iterative deepening with time limit
        Searches depth 1, 2, 3, ... until time runs out
        TT is preserved between depths for better performance
        
        Returns:
            Best move found
        """
        best_move = None
        depth = 1
        
        # Don't clear TT - reuse info from previous depths!
        print(f"[AI] 🔄 Starting iterative deepening (max depth={self.max_depth})")
        
        while depth <= self.max_depth:
            if time.time() - start_time >= self.time_limit:
                print(f"[AI] ⏱️ Time limit reached at depth {depth}")
                break
            
            print(f"[AI] 🔍 Searching depth {depth}...")
            
            current_move = self.get_best_move_at_depth(depth, start_time)
            
            if current_move:
                best_move = current_move
                print(f"[AI] ✅ Depth {depth} complete: {best_move}")
            
            # Check if we should continue
            if time.time() - start_time >= self.time_limit * 0.8:
                print(f"[AI] ⏱️ 80% time used, stopping at depth {depth}")
                break
            
            depth += 1
        
        return best_move if best_move else self.get_fallback_move()
    
    def get_best_move_at_depth(self, depth, start_time):
        """
        Find best move at specific depth
        """
        legal_moves = self.get_threat_space_moves()
        
        if not legal_moves:
            return None
        
        # Quick win/block check
        for move in legal_moves:
            if self.is_winning_move(move, self.player):
                return move
        
        for move in legal_moves:
            if self.is_winning_move(move, self.opponent):
                return move
        
        # Check TT for best move hint from previous depth
        _, tt_best_move = self.transposition_table.lookup(
            self.game.board, depth, float('-inf'), float('inf')
        )
        
        # Order moves intelligently (TT best move gets highest priority)
        ordered_moves = self.advanced_move_ordering(legal_moves, tt_best_move)
        
        best_score = float('-inf')
        best_move = ordered_moves[0]
        alpha = float('-inf')
        beta = float('inf')
        
        for move in ordered_moves:
            # Time check
            if time.time() - start_time >= self.time_limit:
                break
            
            row, col = move
            
            # Make move
            original = self.game.board[row][col]
            self.game.board[row][col] = self.player
            
            # Evaluate
            score = self.minimax(depth - 1, alpha, beta, False, start_time)
            
            # Undo move
            self.game.board[row][col] = original
            
            # Update best
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
        
        # Store in transposition table
        self.transposition_table.store(
            self.game.board, depth, best_score, 'exact', best_move
        )
        
        return best_move
    
    def get_best_move(self):
        """
        Legacy method for fixed depth search
        """
        return self.get_best_move_at_depth(self.max_depth, time.time())
    
    def minimax(self, depth, alpha, beta, maximizing, start_time):
        """
        Minimax with alpha-beta pruning and transposition table
        """
        self.nodes_evaluated += 1
        
        # Time check
        if time.time() - start_time >= self.time_limit:
            return self.evaluate_board()
        
        # Check transposition table
        tt_score, tt_move = self.transposition_table.lookup(
            self.game.board, depth, alpha, beta
        )
        
        if tt_score is not None:
            self.transposition_hits += 1
            self.transposition_cutoffs += 1
            return tt_score
        
        # Terminal conditions
        if depth == 0:
            return self.evaluate_board()
        
        if self.is_game_over():
            winner = self.get_winner()
            if winner == self.player:
                return self.FIVE + depth  # Prefer faster wins
            elif winner == self.opponent:
                return -self.FIVE - depth
            return 0
        
        # Get moves in threat space
        legal_moves = self.get_threat_space_moves()
        if not legal_moves:
            return 0
        
        # Order moves with TT hint
        legal_moves = self.advanced_move_ordering(legal_moves, tt_move)
        
        best_move = None
        
        if maximizing:
            max_eval = float('-inf')
            flag = 'upper'
            
            for move in legal_moves:
                row, col = move
                
                original = self.game.board[row][col]
                self.game.board[row][col] = self.player
                
                eval_score = self.minimax(depth - 1, alpha, beta, False, start_time)
                
                self.game.board[row][col] = original
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    flag = 'lower'
                    break
            
            # Store in TT
            if max_eval > float('-inf'):
                if flag == 'lower' or (beta > alpha):
                    flag = 'exact' if max_eval <= beta else flag
                self.transposition_table.store(
                    self.game.board, depth, max_eval, flag, best_move
                )
            
            return max_eval
        else:
            min_eval = float('inf')
            flag = 'lower'
            
            for move in legal_moves:
                row, col = move
                
                original = self.game.board[row][col]
                self.game.board[row][col] = self.opponent
                
                eval_score = self.minimax(depth - 1, alpha, beta, True, start_time)
                
                self.game.board[row][col] = original
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    flag = 'upper'
                    break
            
            # Store in TT
            if min_eval < float('inf'):
                if flag == 'upper' or (beta > alpha):
                    flag = 'exact' if min_eval >= alpha else flag
                self.transposition_table.store(
                    self.game.board, depth, min_eval, flag, best_move
                )
            
            return min_eval
    
    def evaluate_board(self):
        """
        Evaluate board position
        """
        ai_score = self.count_patterns(self.player)
        opp_score = self.count_patterns(self.opponent)
        return ai_score - opp_score
    
    def count_patterns(self, player):
        """
        Count patterns for player
        """
        score = 0
        board = self.game.board
        size = self.game.board_size
        
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        checked = set()
        
        for row in range(size):
            for col in range(size):
                if board[row][col] != player:
                    continue
                
                for dr, dc in directions:
                    key = (row, col, dr, dc)
                    if key in checked:
                        continue
                    
                    length = 0
                    r, c = row, col
                    
                    while (0 <= r < size and 0 <= c < size and 
                           board[r][c] == player):
                        length += 1
                        checked.add((r, c, dr, dc))
                        r += dr
                        c += dc
                    
                    # Check blocking
                    start_r, start_c = row - dr, col - dc
                    start_blocked = not (0 <= start_r < size and 0 <= start_c < size) or \
                                   board[start_r][start_c] != ' '
                    
                    end_r, end_c = row + dr * length, col + dc * length
                    end_blocked = not (0 <= end_r < size and 0 <= end_c < size) or \
                                 board[end_r][end_c] != ' '
                    
                    # Score pattern
                    if length >= 5:
                        score += self.FIVE
                    elif length == 4:
                        score += self.OPEN_FOUR if not (start_blocked or end_blocked) else self.BLOCKED_FOUR
                    elif length == 3:
                        score += self.OPEN_THREE if not (start_blocked or end_blocked) else self.BLOCKED_THREE
                    elif length == 2:
                        score += self.OPEN_TWO if not (start_blocked or end_blocked) else self.BLOCKED_TWO
        
        return score
    
    def get_threat_space_moves(self, radius=2):
        """
        Get moves in threat space (near existing stones)
        MAJOR OPTIMIZATION: Reduces branching factor dramatically
        """
        moves = set()
        board = self.game.board
        size = self.game.board_size
        
        # Empty board - return center
        if all(board[r][c] == ' ' for r in range(size) for c in range(size)):
            return [(size // 2, size // 2)]
        
        # Find all occupied positions
        for row in range(size):
            for col in range(size):
                if board[row][col] != ' ':
                    # Add neighbors within radius
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            r, c = row + dr, col + dc
                            if (0 <= r < size and 0 <= c < size and 
                                board[r][c] == ' '):
                                moves.add((r, c))
        
        return list(moves)
    
    def advanced_move_ordering(self, moves, tt_best_move=None):
        """
        Advanced move ordering for better alpha-beta pruning
        Priority: TT Best Move > Win > Block > Threats > Proximity
        """
        if not moves:
            return moves
        
        scored_moves = []
        
        for move in moves:
            score = 0
            
            # 0. TT best move from previous search (HIGHEST priority)
            if tt_best_move and move == tt_best_move:
                score += 10000000
            
            # 1. Winning moves
            if self.is_winning_move(move, self.player):
                score += 1000000
            
            # 2. Blocking opponent wins
            elif self.is_winning_move(move, self.opponent):
                score += 100000
            
            # 3. Threat creation
            threat_score = self.evaluate_move_threats(move)
            score += threat_score
            
            # 4. Proximity to stones
            proximity = self.get_proximity_score(move)
            score += proximity
            
            scored_moves.append((score, move))
        
        # Sort descending
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in scored_moves]
    
    def evaluate_move_threats(self, move):
        """
        Evaluate threats created by this move
        """
        row, col = move
        score = 0
        
        # Simulate move
        original = self.game.board[row][col]
        self.game.board[row][col] = self.player
        
        # Count what patterns this creates
        patterns = self.analyze_position_patterns(row, col, self.player)
        
        # Score threats
        if 'OPEN_FOUR' in patterns:
            score += 5000
        if 'BLOCKED_FOUR' in patterns:
            score += 2000
        if 'OPEN_THREE' in patterns:
            score += 500
        if 'BLOCKED_THREE' in patterns:
            score += 100
        
        # Undo
        self.game.board[row][col] = original
        
        return score
    
    def analyze_position_patterns(self, row, col, player):
        """
        Analyze what patterns exist at this position
        """
        patterns = []
        board = self.game.board
        size = self.game.board_size
        
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            length = 1  # Count current position
            
            # Count forward
            r, c = row + dr, col + dc
            while (0 <= r < size and 0 <= c < size and board[r][c] == player):
                length += 1
                r += dr
                c += dc
            front_blocked = not (0 <= r < size and 0 <= c < size) or board[r][c] != ' '
            
            # Count backward
            r, c = row - dr, col - dc
            while (0 <= r < size and 0 <= c < size and board[r][c] == player):
                length += 1
                r -= dr
                c -= dc
            back_blocked = not (0 <= r < size and 0 <= c < size) or board[r][c] != ' '
            
            # Classify pattern
            if length >= 4:
                if not front_blocked and not back_blocked:
                    patterns.append('OPEN_FOUR')
                else:
                    patterns.append('BLOCKED_FOUR')
            elif length == 3:
                if not front_blocked and not back_blocked:
                    patterns.append('OPEN_THREE')
                else:
                    patterns.append('BLOCKED_THREE')
        
        return patterns
    
    def get_proximity_score(self, move):
        """
        Score based on proximity to existing stones
        """
        row, col = move
        min_dist = float('inf')
        
        for r in range(self.game.board_size):
            for c in range(self.game.board_size):
                if self.game.board[r][c] != ' ':
                    dist = abs(row - r) + abs(col - c)
                    min_dist = min(min_dist, dist)
        
        # Closer is better (max score 10)
        return max(0, 10 - min_dist)
    
    def is_winning_move(self, move, player):
        """Check if move wins immediately"""
        row, col = move
        original = self.game.board[row][col]
        self.game.board[row][col] = player
        is_win = self.game.check_winner(row, col, player)
        self.game.board[row][col] = original
        return is_win
    
    def is_game_over(self):
        """Check if game ended"""
        return self.game.game_over
    
    def get_winner(self):
        """Get winner"""
        return self.game.winner if self.game.game_over else None
    
    def get_fallback_move(self):
        """Emergency fallback move"""
        moves = self.get_threat_space_moves()
        return moves[0] if moves else (7, 7)
