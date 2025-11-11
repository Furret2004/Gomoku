"""
Minimax AI with Alpha-Beta Pruning for Gomoku
Implements strategic gameplay using search algorithms
"""

import copy
from typing import Tuple, List, Optional
import enum
import random

class Pattern(enum.Enum):
    NONE = 0
    FIVE = 1
    OPEN_FOUR = 2
    BLOCKED_FOUR = 3
    OPEN_THREE = 4
    BLOCKED_THREE = 5
    OPEN_TWO = 6
    BLOCKED_TWO = 7

class MinimaxAI:
    """
    Minimax AI with alpha-beta pruning for Gomoku
    Evaluates board positions using pattern-based heuristics
    """

    SCORE_MAP = {
        Pattern.FIVE: 100000,
        Pattern.OPEN_FOUR: 10000,
        Pattern.BLOCKED_FOUR: 5000,
        Pattern.OPEN_THREE: 1000,
        Pattern.BLOCKED_THREE: 100,
        Pattern.OPEN_TWO: 10,
        Pattern.BLOCKED_TWO: 1,
        Pattern.NONE: 0,
    }
    
    PATTERN_LOOKUP_TABLE = {}
    DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

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
        self.players_map = {self.player: 1, self.opponent: 2, ' ': 0}
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.nodes_evaluated = 0
        self.board_score_cache = {}
        
        self.potential_lines = {}
        self.current_board_score = 0
        self.zobrist_keys = self._initialize_zobrist()
        self.current_hash = 0
        
        if not MinimaxAI.PATTERN_LOOKUP_TABLE:
            MinimaxAI._initialize_lookup_table()
            
        self.initialize_ai_state()

    def _initialize_zobrist(self):
        size = self.game.board_size
        keys = [[[0, 0] for _ in range(size)] for _ in range(size)]
        for r in range(size):
            for c in range(size):
                keys[r][c][0] = random.getrandbits(64)
                keys[r][c][1] = random.getrandbits(64)
        return keys

    @staticmethod
    def _initialize_lookup_table():
        import itertools
        for line_tuple in itertools.product([0, 1, 2], repeat=9):
            patterns = [Pattern.NONE, Pattern.NONE]
            
            line_str_p1 = "".join(['P' if c == 1 else 'O' if c == 2 else ' ' for c in line_tuple])
            patterns[0] = MinimaxAI._classify_line_string(line_str_p1, 'P')
            
            line_str_p2 = "".join(['P' if c == 2 else 'O' if c == 1 else ' ' for c in line_tuple])
            patterns[1] = MinimaxAI._classify_line_string(line_str_p2, 'P')

            MinimaxAI.PATTERN_LOOKUP_TABLE[line_tuple] = patterns

    @staticmethod
    def _classify_line_string(line_str, player):
        opponent_char = 'O'
        if player * 5 in line_str: return Pattern.FIVE
        if f' {player*4} ' in line_str.replace(opponent_char, '#'): return Pattern.OPEN_FOUR
        
        if f' {player*3} ' in line_str.replace(opponent_char, '#'):
             if line_str.count(f'{player} {player*2}') > 0 and line_str.count(opponent_char) == 0:
                 return Pattern.BLOCKED_FOUR
             if line_str.count(f'{player*2} {player}') > 0 and line_str.count(opponent_char) == 0:
                 return Pattern.BLOCKED_FOUR
             return Pattern.OPEN_THREE

        s_line_space = line_str.replace(' ', '#')
        if f'#{player*4}' in s_line_space or f'{player*4}#' in s_line_space: return Pattern.BLOCKED_FOUR
        if f'{player}{" "}{player*3}' in line_str or f'{player*3}{" "}{player}' in line_str or f'{player*2}{" "}{player*2}' in line_str:
            if opponent_char not in line_str: return Pattern.BLOCKED_FOUR
        
        if (f'#{player*3} ' in s_line_space and ' ' in line_str) or (f' {player*3}#' in s_line_space and ' ' in line_str) or (f'#{player} {player*2}#' in s_line_space) or (f'#{player*2} {player}#' in s_line_space):
            return Pattern.BLOCKED_THREE

        if f' {player*2} ' in line_str.replace(opponent_char, '#'): return Pattern.OPEN_TWO
        if (f'#{player*2} ' in s_line_space and ' ' in line_str) or (f' {player*2}#' in s_line_space and ' ' in line_str): return Pattern.BLOCKED_TWO
            
        return Pattern.NONE

    def initialize_ai_state(self):
        size = self.game.board_size
        self.potential_lines.clear()
        self.current_board_score = 0
        self.current_hash = 0
        
        empty_line_hash = tuple([0] * 9)
        empty_patterns = self.PATTERN_LOOKUP_TABLE[empty_line_hash]

        for r in range(size):
            for c in range(size):
                for dir_idx in range(4):
                    self.potential_lines[(r, c, dir_idx)] = list(empty_patterns)
        
        for r in range(size):
            for c in range(size):
                piece = self.game.board[r][c]
                if piece != ' ':
                    self._update_hash_and_scores_for_piece(r, c, piece)
    
    def _update_hash_and_scores_for_piece(self, row, col, piece):
        player_idx = 0 if piece == self.player else 1
        self.current_hash ^= self.zobrist_keys[row][col][player_idx]

        for dir_idx in range(4):
            line = self._get_line_at(row, col, dir_idx)
            old_patterns = self.potential_lines[(row, col, dir_idx)]
            self.current_board_score -= (self.SCORE_MAP[old_patterns[0]] - self.SCORE_MAP[old_patterns[1]])
            
            line_tuple = self._line_to_tuple(line)
            new_patterns = self.PATTERN_LOOKUP_TABLE[line_tuple]
            self.potential_lines[(row, col, dir_idx)] = list(new_patterns)
            self.current_board_score += (self.SCORE_MAP[new_patterns[0]] - self.SCORE_MAP[new_patterns[1]])

    def _apply_move(self, move: Tuple[int, int], player_char: str) -> List:
        row, col = move
        size = self.game.board_size
        player_idx = 0 if player_char == self.player else 1
        
        self.game.board[row][col] = player_char
        self.current_hash ^= self.zobrist_keys[row][col][player_idx]

        undo_info = []

        for dir_idx, (dr, dc) in enumerate(self.DIRECTIONS):
            for i in range(-4, 5):
                nr, nc = row + i * dr, col + i * dc
                if 0 <= nr < size and 0 <= nc < size:
                    line = self._get_line_at(nr, nc, dir_idx)
                    old_patterns = self.potential_lines[(nr, nc, dir_idx)]
                    undo_info.append(((nr, nc, dir_idx), list(old_patterns)))
                    
                    self.current_board_score -= (self.SCORE_MAP[old_patterns[0]] - self.SCORE_MAP[old_patterns[1]])
                    
                    line_tuple = self._line_to_tuple(line)
                    new_patterns = self.PATTERN_LOOKUP_TABLE[line_tuple]
                    self.potential_lines[(nr, nc, dir_idx)] = list(new_patterns)
                    self.current_board_score += (self.SCORE_MAP[new_patterns[0]] - self.SCORE_MAP[new_patterns[1]])

        return undo_info
        
    def _undo_move(self, move: Tuple[int, int], player_char: str, undo_info: List):
        row, col = move
        player_idx = 0 if player_char == self.player else 1
        
        self.game.board[row][col] = ' '
        self.current_hash ^= self.zobrist_keys[row][col][player_idx]

        for line_key, old_patterns in undo_info:
            current_patterns = self.potential_lines[line_key]
            self.current_board_score -= (self.SCORE_MAP[current_patterns[0]] - self.SCORE_MAP[current_patterns[1]])
            self.potential_lines[line_key] = old_patterns
            self.current_board_score += (self.SCORE_MAP[old_patterns[0]] - self.SCORE_MAP[old_patterns[1]])

    def _get_line_at(self, row, col, dir_idx):
        dr, dc = self.DIRECTIONS[dir_idx]
        line = []
        for i in range(-4, 5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < self.game.board_size and 0 <= c < self.game.board_size:
                line.append(self.game.board[r][c])
            else:
                line.append(None) # Out of board symbol
        return line

    def _line_to_tuple(self, line_cells):
        val = 0
        for cell in line_cells:
            val *= 3
            if cell is not None:
                val += self.players_map.get(cell, 0)
        
        line = [0] * 9
        for i in range(8, -1, -1):
            line[i] = val % 3
            val //= 3
        return tuple(line)

    def make_move(self) -> Optional[Tuple[int, int]]:
        """
        Find and return the best move using minimax algorithm
        
        Returns:
            (row, col) tuple or None if no valid moves
        """
        self.nodes_evaluated = 0
        self.board_score_cache.clear()
        
        best_move = self.get_best_move()
        print(f"[AI] Evaluated {self.nodes_evaluated} nodes, depth={self.depth}")
        print(f"[AI] Cache size: {len(self.board_score_cache)} positions")

        if best_move:
             self._apply_move(best_move, self.player)

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

        for move in legal_moves:
            if self.is_winning_move(move, self.player):
                return move

        winning_block = None
        for move in legal_moves:
            if self.is_winning_move(move, self.opponent):
                winning_block = move
                break
        if winning_block:
             return winning_block

        ordered_moves = self.order_moves(legal_moves)
        best_score = float('-inf')
        best_move = ordered_moves[0]
        alpha = float('-inf')
        beta = float('inf')

        for move in ordered_moves:
            undo_info = self._apply_move(move, self.player)
            score = self.minimax(self.depth - 1, alpha, beta, False)
            self._undo_move(move, self.player, undo_info)
            
            if score > best_score:
                best_score = score
                best_move = move
            
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
        original_alpha = alpha
        if self.current_hash in self.board_score_cache:
            cached_score, cached_depth, flag = self.board_score_cache[self.current_hash]
            if cached_depth >= depth:
                if flag == 'EXACT': return cached_score
                if flag == 'LOWERBOUND': alpha = max(alpha, cached_score)
                elif flag == 'UPPERBOUND': beta = min(beta, cached_score)
                if alpha >= beta: return cached_score

        self.nodes_evaluated += 1
        
        winner = self.game.winner
        if winner:
            return self.SCORE_MAP[Pattern.FIVE] if winner == self.player else -self.SCORE_MAP[Pattern.FIVE]

        if self.is_board_full():
            return 0

        if depth == 0:
            return self.evaluate_board()
        
        legal_moves = self.get_legal_moves_nearby()
        if not legal_moves:
            return 0
        
        ordered_moves = self.order_moves(legal_moves)
        
        if maximizing:
            max_eval = float('-inf')
            current_player = self.player
        else:
            min_eval = float('inf')
            current_player = self.opponent
            
        for move in ordered_moves:
            original_winner = self.game.winner
            
            undo_info = self._apply_move(move, current_player)
            if self.is_winning_move(move, current_player): self.game.winner = current_player

            eval_score = self.minimax(depth - 1, alpha, beta, not maximizing)
            
            self.game.winner = original_winner
            self._undo_move(move, current_player, undo_info)

            if maximizing:
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            else:
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha: break

        result = max_eval if maximizing else min_eval
        
        flag = 'EXACT'
        if result <= original_alpha: flag = 'UPPERBOUND'
        elif result >= beta: flag = 'LOWERBOUND'
        self.board_score_cache[self.current_hash] = (result, depth, flag)

        return result

    def evaluate_board(self) -> float:
        """
        Evaluate current board position using pattern-based heuristics
        
        Returns:
            Score (positive = good for AI, negative = good for opponent)
        """
        return self.current_board_score

    def get_legal_moves_nearby(self, radius=2):
        moves = set()
        board = self.game.board
        size = self.game.board_size
        
        has_stones = any(board[r][c] != ' ' for r in range(size) for c in range(size))
        if not has_stones: return [(size // 2, size // 2)]
        
        for row in range(size):
            for col in range(size):
                if board[row][col] == ' ':
                    is_neighbor = False
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            if dr == 0 and dc == 0: continue
                            r, c = row + dr, col + dc
                            if 0 <= r < size and 0 <= c < size and board[r][c] != ' ':
                                moves.add((row, col))
                                is_neighbor = True
                                break
                        if is_neighbor: break
        return list(moves)

    def is_board_full(self):
        return ' ' not in (c for r in self.game.board for c in r)

    def order_moves(self, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Order moves by their immediate impact using potential lines
        
        Args:
            moves: List of (row, col) moves
            
        Returns:
            Ordered list of moves
        """
        scored_moves = []
        for move in moves:
            score = 0
            
            # AI's potential threat
            self.game.board[move[0]][move[1]] = self.player
            for dir_idx in range(4):
                line = self._get_line_at(move[0], move[1], dir_idx)
                line_tuple = self._line_to_tuple(line)
                patterns = self.PATTERN_LOOKUP_TABLE[line_tuple]
                score += self.SCORE_MAP[patterns[0]]
            self.game.board[move[0]][move[1]] = ' '
            
            # Blocking opponent's potential threat
            self.game.board[move[0]][move[1]] = self.opponent
            for dir_idx in range(4):
                line = self._get_line_at(move[0], move[1], dir_idx)
                line_tuple = self._line_to_tuple(line)
                patterns = self.PATTERN_LOOKUP_TABLE[line_tuple]
                score += self.SCORE_MAP[patterns[1]] * 0.9 # Slightly less important than attacking
            self.game.board[move[0]][move[1]] = ' '

            scored_moves.append((score, move))
            
        scored_moves.sort(key=lambda x: x[0], reverse=True)
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
        self.game.board[row][col] = player
        is_win = self.game.check_winner(row, col, player)
        self.game.board[row][col] = ' '
        return is_win

    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.game.game_over or not self.get_legal_moves_nearby()

    def get_winner(self) -> Optional[str]:
        """Get winner if game is over"""
        return self.game.winner if self.game.game_over else None


