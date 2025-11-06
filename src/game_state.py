"""
Game State Manager - Save and Load game state
Handles serialization of game state to JSON
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any


class GameStateManager:
    """
    Manages game state persistence (save/load functionality)
    """
    
    DEFAULT_SAVE_DIR = 'saves'
    DEFAULT_SAVE_FILE = 'gomoku_save.json'
    
    @staticmethod
    def ensure_save_directory():
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(GameStateManager.DEFAULT_SAVE_DIR):
            os.makedirs(GameStateManager.DEFAULT_SAVE_DIR)
    
    @staticmethod
    def save_game(game, game_mode='singleplayer', ai_difficulty='Medium', 
                  filename=None) -> bool:
        """
        Save current game state to file
        
        Args:
            game: GomokuGame instance
            game_mode: 'singleplayer' or 'multiplayer'
            ai_difficulty: AI difficulty level (for singleplayer)
            filename: Optional custom filename
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            GameStateManager.ensure_save_directory()
            
            if filename is None:
                filename = os.path.join(
                    GameStateManager.DEFAULT_SAVE_DIR,
                    GameStateManager.DEFAULT_SAVE_FILE
                )
            
            # Serialize game state
            state = {
                'board': GameStateManager.serialize_board(game.board),
                'board_size': game.board_size,
                'current_player': game.current_player,
                'game_mode': game_mode,
                'ai_difficulty': ai_difficulty,
                'game_over': game.game_over,
                'winner': game.winner,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            print(f"[Save] Game saved to {filename}")
            return True
            
        except Exception as e:
            print(f"[Save Error] Failed to save game: {e}")
            return False
    
    @staticmethod
    def load_game(filename=None) -> Optional[Dict[str, Any]]:
        """
        Load game state from file
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Dictionary with game state or None if load failed
        """
        try:
            if filename is None:
                filename = os.path.join(
                    GameStateManager.DEFAULT_SAVE_DIR,
                    GameStateManager.DEFAULT_SAVE_FILE
                )
            
            if not os.path.exists(filename):
                print(f"[Load] No save file found: {filename}")
                return None
            
            # Read from file
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Deserialize board
            state['board'] = GameStateManager.deserialize_board(state['board'])
            
            print(f"[Load] Game loaded from {filename}")
            return state
            
        except Exception as e:
            print(f"[Load Error] Failed to load game: {e}")
            return None
    
    @staticmethod
    def has_saved_game(filename=None) -> bool:
        """
        Check if a saved game exists
        
        Args:
            filename: Optional custom filename
            
        Returns:
            True if save file exists
        """
        if filename is None:
            filename = os.path.join(
                GameStateManager.DEFAULT_SAVE_DIR,
                GameStateManager.DEFAULT_SAVE_FILE
            )
        
        return os.path.exists(filename)
    
    @staticmethod
    def delete_saved_game(filename=None) -> bool:
        """
        Delete a saved game file
        
        Args:
            filename: Optional custom filename
            
        Returns:
            True if deletion successful
        """
        try:
            if filename is None:
                filename = os.path.join(
                    GameStateManager.DEFAULT_SAVE_DIR,
                    GameStateManager.DEFAULT_SAVE_FILE
                )
            
            if os.path.exists(filename):
                os.remove(filename)
                print(f"[Delete] Saved game deleted: {filename}")
                return True
            return False
            
        except Exception as e:
            print(f"[Delete Error] Failed to delete save: {e}")
            return False
    
    @staticmethod
    def serialize_board(board) -> list:
        """
        Convert 2D board to serializable format
        
        Args:
            board: 2D list representing the board
            
        Returns:
            Serialized board (list of lists)
        """
        return [row[:] for row in board]
    
    @staticmethod
    def deserialize_board(data) -> list:
        """
        Convert serialized data back to board format
        
        Args:
            data: Serialized board data
            
        Returns:
            2D list representing the board
        """
        return [row[:] for row in data]
    
    @staticmethod
    def get_save_info(filename=None) -> Optional[Dict[str, str]]:
        """
        Get information about a saved game without loading it
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Dictionary with save info or None
        """
        try:
            if filename is None:
                filename = os.path.join(
                    GameStateManager.DEFAULT_SAVE_DIR,
                    GameStateManager.DEFAULT_SAVE_FILE
                )
            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            return {
                'timestamp': state.get('timestamp', 'Unknown'),
                'game_mode': state.get('game_mode', 'Unknown'),
                'ai_difficulty': state.get('ai_difficulty', 'N/A'),
                'current_player': state.get('current_player', 'Unknown')
            }
            
        except Exception as e:
            print(f"[Info Error] Failed to get save info: {e}")
            return None
