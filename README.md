# Gomoku Game

Game cờ Gomoku (5 in a row) với AI thông minh và chế độ multiplayer.

## Yêu cầu
- Python 3.7 trở lên
- Tkinter (thường có sẵn với Python)

## Cách chơi

### Khởi động game
```bash
python main.py
```

### Chế độ chơi
- **Play vs AI**: Chơi với máy (4 độ khó: Easy, Medium, Hard, Expert, Expert+)
- **Play vs Player**: Chơi online với người khác
- **Statistics**: Xem thống kê game

### Multiplayer
Server:
```bash
python start_server.py
```

Client:
```bash
python start_client.py
```

## Tính năng
- AI với Minimax algorithm + Alpha-Beta pruning
- Opening Book với 4 khai cuộc nổi tiếng
- Transposition Table với Zobrist hashing
- Iterative Deepening search
- Save/Load game
- Thống kê trận đấu
- Pause/Resume game