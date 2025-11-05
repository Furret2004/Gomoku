import random
import copy

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
    
class MinimaxAI:
    def __init__(self, game, player_symbol, opponent_symbol, depth=3):
        self.game = game
        self.player_symbol = player_symbol
        self.opponent_symbol = opponent_symbol
        self.depth = depth
        self.board_size = len(game.board)  

    def get_best_move(self):
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        valid_moves = self.game.get_valid_moves()  
        if not valid_moves:
            return None
        
        valid_moves = sorted(valid_moves, key=self.move_heuristic)
        
        for move in valid_moves:
            old_val = self.game.board[move[0]][move[1]]
            self.game.board[move[0]][move[1]] = self.player_symbol
            move_value = self.minimax(self.game.board, self.depth - 1, alpha, beta, maximizing=False)
            self.game.board[move[0]][move[1]] = old_val

            if move_value > best_value:
                best_value = move_value
                best_move = move
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing):
        winner = self.check_terminal_state(board)
        if winner:
            if winner == self.player_symbol:
                return 1000000  
            elif winner == self.opponent_symbol:
                return -1000000  
            else: 
                return 0
        
        if depth <= 0:
            return self.evaluate_board(board)

        valid_moves = self.get_smart_valid_moves(board)
        if maximizing:  
            max_eval = -float('inf')
            for move in sorted(valid_moves, key=self.move_heuristic):
                old_val = board[move[0]][move[1]]
                board[move[0]][move[1]] = self.player_symbol
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board[move[0]][move[1]] = old_val
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, max_eval)
                if alpha >= beta:
                    break
            return max_eval
        else:  
            min_eval = float('inf')
            for move in sorted(valid_moves, key=self.move_heuristic):
                old_val = board[move[0]][move[1]]
                board[move[0]][move[1]] = self.opponent_symbol
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board[move[0]][move[1]] = old_val
                min_eval = min(min_eval, eval_score)
                beta = min(beta, min_eval)
                if alpha >= beta:
                    break
            return min_eval

    def evaluate_board(self, board):
        player_score = self.calculate_score(board, self.player_symbol)
        opponent_score = self.calculate_score(board, self.opponent_symbol)
        return player_score - opponent_score * 1.5

    def calculate_score(self, board, player):
        score = 0
        opponent = self.opponent_symbol if player == self.player_symbol else self.player_symbol
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(self.board_size):
            for c in range(self.board_size):
                if board[r][c] == player:
                    for dr, dc in directions:
                        line = self.get_line(board, r, c, dr, dc)
                        score += self.score_line(line, player, opponent)
        return score // 4 

    def get_line(self, board, r, c, dr, dc):
        line = [board[r][c]]
        nr, nc = r + dr, c + dc
        while 0 <= nr < self.board_size and 0 <= nc < self.board_size:
            line.append(board[nr][nc])
            nr += dr
            nc += dc
        nr, nc = r - dr, c - dc
        while 0 <= nr < self.board_size and 0 <= nc < self.board_size:
            line.insert(0, board[nr][nc])
            nr -= dr
            nc -= dc
        return line

    def score_line(self, line, player, opponent):
        score = 0
        patterns = {5: 100000, 4: 5000, 3: 500, 2: 50}
        open_bonus = {4: 5000, 3: 500, 2: 0}  
        
        i = 0
        n = len(line)
        while i < n:
            if line[i] == player:
                streak_start = i
                while i < n and line[i] == player:
                    i += 1
                streak_len = i - streak_start
                
                if streak_len >= 5:
                    score += patterns[5]
                    continue
                
                left_open = (streak_start > 0 and line[streak_start - 1] == ' ')
                right_open = (i < n and line[i] == ' ')
                num_open = sum([left_open, right_open])
                
                base_score = patterns.get(streak_len, 0)
                if num_open == 2: 
                    score += base_score + open_bonus.get(streak_len, 0)
                elif num_open == 1:
                    score += base_score // 2
                else:  
                    score += base_score // 4
            else:
                i += 1
        return score

    def move_heuristic(self, move):
        r, c = move
        center_dist = abs(r - self.board_size // 2) + abs(c - self.board_size // 2)
        return -center_dist  

    def get_smart_valid_moves(self, board):
        moves = set()
        has_pieces = any(any(cell != ' ' for cell in row) for row in board)
        if not has_pieces:
            center_r, center_c = self.board_size // 2, self.board_size // 2
            for dr in range(-3, 4):
                for dc in range(-3, 4):
                    nr, nc = center_r + dr, center_c + dc
                    if 0 <= nr < self.board_size and 0 <= nc < self.board_size and board[nr][nc] == ' ':
                        moves.add((nr, nc))
            return sorted(list(moves), key=self.move_heuristic)
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board[r][c] != ' ':
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.board_size and 0 <= nc < self.board_size and board[nr][nc] == ' ':
                                moves.add((nr, nc))
        
        moves_list = list(moves)
        if len(moves_list) < 30:
            center_r, center_c = self.board_size // 2, self.board_size // 2
            for dist in range(5):  
                for dr in range(-dist, dist + 1):
                    for dc in range(-dist, dist + 1):
                        if abs(dr) + abs(dc) == dist:
                            nr, nc = center_r + dr, center_c + dc
                            if 0 <= nr < self.board_size and 0 <= nc < self.board_size and board[nr][nc] == ' ':
                                moves.add((nr, nc))
                                if len(moves) >= 60:
                                    break
                    if len(moves) >= 60:
                        break
                if len(moves) >= 60:
                    break
            moves_list = list(moves)
        
        return sorted(moves_list, key=self.move_heuristic)[:80]

    def check_terminal_state(self, board):
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board[r][c] != ' ':
                    player = board[r][c]
                    if c + 4 < self.board_size and all(board[r][c + i] == player for i in range(5)):
                        return player
                    if r + 4 < self.board_size and all(board[r + i][c] == player for i in range(5)):
                        return player
                    if r + 4 < self.board_size and c + 4 < self.board_size and all(board[r + i][c + i] == player for i in range(5)):
                        return player
                    if r + 4 < self.board_size and c - 4 >= 0 and all(board[r + i][c - i] == player for i in range(5)):
                        return player
        if all(all(cell != ' ' for cell in row) for row in board):
            return 'draw'
        return None