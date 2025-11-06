# CODE IMPLEMENTATION REPORT

## I. TỔNG QUAN NHỮNG GÌ ĐÃ THỰC HIỆN

###  AI System (4 điểm)
- Implement Minimax/Alpha-Beta AI (+3 điểm)
- Multiple AI Difficulty Levels (+1 điểm)

### Pause/Save System (1 điểm)  
- Game State Management
- Save/Load functionality
- Pause menu with Continue option

### Code Quality & Bug Fixes
- Remove duplicate code
- Add error handling cho network
- Add reconnection logic
- Add game statistics tracking

---

## II. FILES MỚI ĐÃ TẠO

### 1. `src/ai_minimax.py`
**Mục đích:** AI thông minh sử dụng Minimax algorithm với Alpha-Beta pruning

**Các class và methods chính:**

#### Class `MinimaxAI`
```python
class MinimaxAI:
    # Scoring constants
    FIVE = 100000       # Five in a row (win)
    OPEN_FOUR = 10000   # Four in a row with both ends open
    BLOCKED_FOUR = 5000 # Four in a row with one end blocked
    OPEN_THREE = 1000   # Three in a row with both ends open
    BLOCKED_THREE = 100
    OPEN_TWO = 10
    BLOCKED_TWO = 1
```

**Các methods quan trọng:**

1. **`__init__(game, player='O', depth=3, use_alpha_beta=True)`**
   - Khởi tạo AI với độ sâu tìm kiếm
   - Hỗ trợ bật/tắt alpha-beta pruning

2. **`make_move() -> (row, col)`**
   - Entry point để AI đánh nước
   - Trả về tọa độ nước đi tốt nhất
   - Track số nodes đã evaluate

3. **`get_best_move() -> (row, col)`**
   - Tìm nước đi tốt nhất
   - Quick win check: nếu có nước thắng ngay → đánh
   - Quick block check: nếu đối thủ sắp thắng → chặn
   - Order moves theo proximity
   - Chạy minimax cho từng nước đi

4. **`minimax(depth, alpha, beta, maximizing) -> float`**
   - Core algorithm: Minimax với Alpha-Beta pruning
   - Recursive depth-limited search
   - Terminal conditions: depth=0 hoặc game over
   - Maximizing player: AI (chọn max score)
   - Minimizing player: Opponent (chọn min score)
   - Alpha-beta cutoff để tăng tốc

5. **`evaluate_board() -> float`**
   - Heuristic evaluation function
   - Tính: AI_score - Opponent_score
   - Số dương = tốt cho AI, số âm = tốt cho đối thủ

6. **`evaluate_player(player) -> float`**
   - Pattern detection cho 1 player
   - Quét 4 hướng: ngang, dọc, chéo \, chéo /
   - Đếm consecutive stones
   - Kiểm tra blocked/open ends
   - Tính điểm theo pattern scoring table

7. **`order_moves(moves) -> sorted_moves`**
   - Sắp xếp moves theo proximity tới stones hiện có
   - Moves gần stones có khả năng tốt hơn
   - Giảm branching factor cho alpha-beta

8. **`is_winning_move(move, player) -> bool`**
   - Kiểm tra nếu move này thắng ngay
   - Dùng để quick win/block check

---

### 2. `src/ai_manager.py`
**Mục đích:** Quản lý các cấp độ AI khác nhau

#### Class `AIManager`
```python
DIFFICULTIES = {
    'Easy': RandomAI (depth=N/A),
    'Medium': MinimaxAI (depth=2),
    'Hard': MinimaxAI (depth=3),
    'Expert': MinimaxAI (depth=4)
}
```

**Methods:**

1. **`get_ai(game, difficulty, player) -> AI_instance`**
   - Factory method để tạo AI theo difficulty
   - Auto-configure parameters (depth, alpha-beta)
   - Error handling: fallback to Medium nếu invalid

2. **`get_difficulty_list() -> list`**
   - Trả về danh sách difficulties available

3. **`get_description(difficulty) -> string`**
   - Trả về mô tả cho từng difficulty

---

### 3. `src/game_state.py`
**Mục đích:** Save/Load game state vào JSON file

#### Class `GameStateManager`

**Static methods:**

1. **`save_game(game, game_mode, ai_difficulty, filename) -> bool`**
   - Serialize game state to JSON
   - Structure:
     ```json
     {
       "board": [[...], ...],
       "board_size": 15,
       "current_player": "X",
       "game_mode": "singleplayer",
       "ai_difficulty": "Medium",
       "game_over": false,
       "winner": null,
       "timestamp": "2025-11-06T...",
       "version": "1.0"
     }
     ```
   - Auto-create saves/ directory
   - Error handling với try-catch

2. **`load_game(filename) -> dict | None`**
   - Deserialize từ JSON
   - Validate file existence
   - Return None nếu fail

3. **`has_saved_game(filename) -> bool`**
   - Check nếu save file tồn tại
   - Dùng để show/hide Continue button

4. **`delete_saved_game(filename) -> bool`**
   - Xóa saved game

5. **`get_save_info(filename) -> dict | None`**
   - Lấy metadata về saved game
   - Không load full state
   - Dùng để preview save info

6. **`serialize_board(board) -> list`**
   - Convert 2D board thành serializable format

7. **`deserialize_board(data) -> list`**
   - Convert back từ JSON data

**File location:** `saves/gomoku_save.json`

---

### 4. `src/game_statistics.py`
**Mục đích:** Track và persist game statistics

#### Class `GameStatistics`

**Data structure:**
```json
{
  "singleplayer": {
    "total_games": 0,
    "wins": 0,
    "losses": 0,
    "draws": 0,
    "by_difficulty": {
      "Easy": {"games": 0, "wins": 0, "losses": 0, "draws": 0},
      "Medium": {...},
      "Hard": {...},
      "Expert": {...}
    }
  },
  "multiplayer": {
    "total_games": 0,
    "wins": 0,
    "losses": 0,
    "draws": 0
  },
  "history": [...]  // Last 100 games
}
```

**Methods:**

1. **`load_statistics() -> dict`**
   - Load từ `saves/statistics.json`
   - Return default structure nếu không có file

2. **`save_statistics() -> bool`**
   - Persist statistics to disk

3. **`record_game(game_mode, result, difficulty)`**
   - Record kết quả game
   - Update counters
   - Add to history (keep last 100)
   - Auto-save

4. **`get_win_rate(game_mode, difficulty) -> float`**
   - Tính win rate percentage
   - Filter by difficulty nếu provided

5. **`get_statistics_summary() -> string`**
   - Format statistics thành readable text
   - Show overall stats
   - Breakdown by difficulty
   - Multiplayer stats

6. **`reset_statistics()`**
   - Reset về default

**File location:** `saves/statistics.json`

---

## III. FILES ĐÃ CHỈNH SỬA

### 1. `singleplayer.py`

**Changes added:**

#### A. Import statements
```python
from src.ai_manager import AIManager
from src.game_state import GameStateManager
from src.game_statistics import GameStatistics
from tkinter import messagebox, simpledialog, scrolledtext
```

#### B. Constructor changes
```python
def __init__(self, difficulty='Medium'):
    # OLD: self.ai = GomokuAI(self.game)
    # NEW:
    self.difficulty = difficulty
    self.ai = AIManager.get_ai(self.game, self.difficulty, self.ai_symbol)
    self.statistics = GameStatistics()
```

#### C. GUI additions

**1. Difficulty selector:**
```python
difficulty_frame = tk.Frame(top_frame)
tk.Label("AI Difficulty:")
self.difficulty_var = tk.StringVar(value=self.difficulty)
difficulty_menu = tk.OptionMenu(
    difficulty_frame,
    self.difficulty_var,
    *AIManager.get_difficulty_list(),
    command=self.change_difficulty
)
self.diff_info_label = tk.Label(...)  # Description
```

**2. New buttons:**
- Pause button → `pause_game()`
- Save Game button → `save_game()`
- Statistics button → `show_statistics()`

#### D. New methods

**1. `change_difficulty(new_difficulty)`**
- Update AI difficulty
- Show confirmation dialog nếu game đang chơi
- Recreate AI instance

**2. `pause_game()`**
- Pause game
- Show dialog: Continue | Save & Quit
- Temporarily disable game_active

**3. `save_game()`**
- Call GameStateManager.save_game()
- Show success/error message

**4. `save_and_quit()`**
- Save then quit
- Handle save failures

**5. `load_game()`**
- Load game state từ file
- Restore board, difficulty, AI
- Redraw board với loaded state
- Show success message

**6. `show_statistics()`**
- Open new Toplevel window
- Display statistics in ScrolledText
- Buttons: Reset Statistics | Close

**7. `reset_statistics(window)`**
- Confirm dialog
- Call statistics.reset_statistics()

#### E. Statistics tracking
Thêm `statistics.record_game()` vào 3 chỗ:
- Player wins
- AI wins
- Draw (2 places)

#### F. Quit dialog enhancement
```python
def quit_game(self):
    if self.game_active:
        # Ask: Save & Quit | Quit without saving | Cancel
        response = messagebox.askyesnocancel(...)
```

---

### 2. `main.py`

**Changes added:**

#### A. Imports
```python
from src.game_state import GameStateManager
from src.game_statistics import GameStatistics
from tkinter import messagebox, scrolledtext
```

#### B. Continue button
```python
if GameStateManager.has_saved_game():
    continue_button = tk.Button(
        text="▶️ Continue Game",
        command=self.continue_game,
        bg='#27AE60'
    )
```

#### C. Statistics button
```python
stats_button = tk.Button(
    text="📊 Statistics",
    command=self.show_statistics,
    bg='#9B59B6'
)
```

#### D. New methods

**1. `continue_game()`**
- Load save info
- Show preview dialog
- Confirm to continue
- Load game via singleplayer.load_game()

**2. `show_statistics()`**
- Create Toplevel window
- Display statistics summary
- ScrolledText with formatted output

---

### 3. `src/network/client.py`

**Changes added:**

#### A. Constructor
```python
self.reconnect_attempts = 0
self.max_reconnect_attempts = 3
```

#### B. Enhanced error handling

**1. `connect_to_server()` improvements:**
```python
# Added:
self.socket.settimeout(10)  # Connection timeout
# Better error messages:
except socket.timeout:
    messagebox.showerror("Connection Timeout", ...)
except ConnectionRefusedError:
    messagebox.showerror("Connection Refused", ...)
except socket.gaierror:
    messagebox.showerror("Invalid Address", ...)
```

**2. `receive_messages()` improvements:**
```python
# Added:
try:
    message = json.loads(data.decode('utf-8'))
except json.JSONDecodeError:
    print("Invalid JSON")
    continue

# Better exception handling:
except ConnectionResetError:
    self.root.after(0, self.handle_disconnection)
except socket.error as se:
    messagebox.showerror("Network Error", ...)
```

**3. `send_move()` improvements:**
```python
if not self.connected:
    messagebox.showerror("Error", "Not connected")
    return

try:
    # ... send logic
except socket.error as se:
    messagebox.showerror("Network Error", ...)
    self.connected = False
```

#### C. Reconnection logic

**New methods:**

**1. `handle_disconnection()`**
- Show reconnection dialog
- Ask user nếu muốn reconnect
- Track reconnection attempts
- Quit nếu user refuse hoặc max attempts reached

**2. `attempt_reconnect()`**
- Close old socket
- Create new socket with timeout
- Try to reconnect
- Restart receive thread nếu success
- Retry với delay nếu failed
- Show error nếu all attempts failed

**Flow:**
```
Connection Lost → handle_disconnection() → attempt_reconnect()
                                          ↓
                        Success → Resume game
                                          ↓
                        Failed → Retry (max 3 times) → Quit
```

---

### 4. Removed Files

**Deleted:** `menu.py`
- **Lý do:** Duplicate của `main.py`
- **Impact:** Cleaned up codebase, no functionality loss

---

## IV. THAY ĐỔI UI/UX

### 1. SinglePlayer Mode

**Before:**
```
[Status Label]
[Game Board]
[New Game] [Quit]
```

**After:**
```
[AI Difficulty Selector]
[Difficulty Description]
[Status Label]
[Game Board]
[New Game] [Pause] [Save Game] [Statistics] [Quit]
```

### 2. Main Menu

**Before:**
```
GOMOKU
[🤖 Play vs AI]
[👥 Play vs Player]
[Exit]
```

**After:**
```
GOMOKU
[▶️ Continue Game]  ← Only if save exists
[🤖 Play vs AI]
[👥 Play vs Player]
[📊 Statistics]
[Exit]
```

### 3. New Windows

**Statistics Window:**
- Title: "Your Game Statistics"
- ScrolledText with formatted stats
- Buttons: Reset | Close

**Save Preview Dialog:**
- Shows: Date, Difficulty, Current Player
- Confirm before loading

---


## V. WHAT'S NEXT (Future Enhancements)

### Phase 3 Ideas (chưa implement):

1. **3-Player Mode**
   - Max-N algorithm instead of Minimax
   - 3 colors: Black, White, Red
   - Modified networking

2. **Machine Learning AI**
   - CNN-based policy network
   - Train on expert games
   - AlphaZero-style MCTS

3. **Obstacles Variant**
   - Random obstacle placement
   - Modified win detection
   - Visual representation

4. **Advanced Features**
   - Game replay viewer
   - AI vs AI mode
   - Online leaderboard
   - Custom board sizes
   - Sound effects & animations
   - Time controls
   - Tournament mode

---
