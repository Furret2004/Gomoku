"""
Game Statistics Tracker
Tracks wins, losses, and game history
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class GameStatistics:
    """
    Tracks and persists game statistics
    """
    
    STATS_FILE = 'saves/statistics.json'
    
    def __init__(self):
        self.stats = self.load_statistics()
    
    @staticmethod
    def load_statistics() -> Dict:
        """Load statistics from file"""
        try:
            if os.path.exists(GameStatistics.STATS_FILE):
                with open(GameStatistics.STATS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Stats] Error loading statistics: {e}")
        
        # Return default structure
        return {
            'singleplayer': {
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'by_difficulty': {
                    'Easy': {'games': 0, 'wins': 0, 'losses': 0, 'draws': 0},
                    'Medium': {'games': 0, 'wins': 0, 'losses': 0, 'draws': 0},
                    'Hard': {'games': 0, 'wins': 0, 'losses': 0, 'draws': 0},
                    'Expert': {'games': 0, 'wins': 0, 'losses': 0, 'draws': 0}
                }
            },
            'multiplayer': {
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0
            },
            'history': []
        }
    
    def save_statistics(self) -> bool:
        """Save statistics to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(GameStatistics.STATS_FILE), exist_ok=True)
            
            with open(GameStatistics.STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Stats] Error saving statistics: {e}")
            return False
    
    def record_game(self, game_mode: str, result: str, difficulty: Optional[str] = None):
        """
        Record a completed game
        
        Args:
            game_mode: 'singleplayer' or 'multiplayer'
            result: 'win', 'loss', or 'draw'
            difficulty: AI difficulty (for singleplayer)
        """
        timestamp = datetime.now().isoformat()
        
        # Update mode statistics
        mode_stats = self.stats[game_mode]
        mode_stats['total_games'] += 1
        
        if result == 'win':
            mode_stats['wins'] += 1
        elif result == 'loss':
            mode_stats['losses'] += 1
        elif result == 'draw':
            mode_stats['draws'] += 1
        
        # Update difficulty statistics (for singleplayer)
        if game_mode == 'singleplayer' and difficulty:
            diff_stats = mode_stats['by_difficulty'].get(difficulty)
            if diff_stats:
                diff_stats['games'] += 1
                if result == 'win':
                    diff_stats['wins'] += 1
                elif result == 'loss':
                    diff_stats['losses'] += 1
                elif result == 'draw':
                    diff_stats['draws'] += 1
        
        # Add to history
        history_entry = {
            'timestamp': timestamp,
            'mode': game_mode,
            'result': result,
            'difficulty': difficulty
        }
        self.stats['history'].append(history_entry)
        
        # Keep only last 100 games in history
        if len(self.stats['history']) > 100:
            self.stats['history'] = self.stats['history'][-100:]
        
        # Save to file
        self.save_statistics()
    
    def get_win_rate(self, game_mode: str, difficulty: Optional[str] = None) -> float:
        """
        Calculate win rate
        
        Args:
            game_mode: 'singleplayer' or 'multiplayer'
            difficulty: Optional difficulty filter
            
        Returns:
            Win rate as percentage (0-100)
        """
        if game_mode == 'singleplayer' and difficulty:
            stats = self.stats['singleplayer']['by_difficulty'].get(difficulty, {})
        else:
            stats = self.stats[game_mode]
        
        total = stats.get('games', 0) or stats.get('total_games', 0)
        wins = stats.get('wins', 0)
        
        if total == 0:
            return 0.0
        
        return (wins / total) * 100
    
    def get_statistics_summary(self) -> str:
        """
        Get formatted statistics summary
        
        Returns:
            Formatted string with statistics
        """
        sp = self.stats['singleplayer']
        mp = self.stats['multiplayer']
        
        summary = "═" * 50 + "\n"
        summary += "GAME STATISTICS\n"
        summary += "═" * 50 + "\n\n"
        
        # Singleplayer stats
        summary += "SINGLE PLAYER (vs AI):\n"
        summary += f"  Total Games: {sp['total_games']}\n"
        summary += f"  Wins: {sp['wins']} | Losses: {sp['losses']} | Draws: {sp['draws']}\n"
        summary += f"  Win Rate: {self.get_win_rate('singleplayer'):.1f}%\n\n"
        
        # By difficulty
        summary += "  By Difficulty:\n"
        for diff in ['Easy', 'Medium', 'Hard', 'Expert']:
            stats = sp['by_difficulty'][diff]
            if stats['games'] > 0:
                wr = (stats['wins'] / stats['games'] * 100) if stats['games'] > 0 else 0
                summary += f"    {diff:8} - Games: {stats['games']:3} | "
                summary += f"W: {stats['wins']:3} | L: {stats['losses']:3} | "
                summary += f"Win Rate: {wr:5.1f}%\n"
        
        # Multiplayer stats
        summary += f"\nMULTIPLAYER (vs Players):\n"
        summary += f"  Total Games: {mp['total_games']}\n"
        summary += f"  Wins: {mp['wins']} | Losses: {mp['losses']} | Draws: {mp['draws']}\n"
        summary += f"  Win Rate: {self.get_win_rate('multiplayer'):.1f}%\n"
        
        summary += "\n" + "═" * 50
        
        return summary
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.stats = self.load_statistics()
        self.save_statistics()
