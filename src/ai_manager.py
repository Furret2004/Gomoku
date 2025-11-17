"""
AI Manager - Central management for different AI difficulty levels
"""

from src.ai import GomokuAI as RandomAI
from src.ai_minimax import MinimaxAI
from src.ai_minimax_optimized import MinimaxAI as OptimizedMinimaxAI


class AIManager:
    """
    Manages different AI difficulty levels for Gomoku
    """
    
    # Difficulty configurations
    DIFFICULTIES = {
        'Easy': {
            'ai_class': RandomAI,
            'description': 'Random moves - Good for beginners',
            'kwargs': {}
        },
        'Medium': {
            'ai_class': OptimizedMinimaxAI,
            'description': 'Strategic AI - Balanced gameplay ⚡',
            'kwargs': {'depth': 2, 'time_limit': 2.0, 'use_iterative_deepening': True}
        },
        'Hard': {
            'ai_class': OptimizedMinimaxAI,
            'description': 'Advanced AI - Challenging opponent ⚡',
            'kwargs': {'depth': 3, 'time_limit': 3.0, 'use_iterative_deepening': True}
        },
        'Expert': {
            'ai_class': OptimizedMinimaxAI,
            'description': 'Master level - Maximum challenge ⚡',
            'kwargs': {'depth': 4, 'time_limit': 5.0, 'use_iterative_deepening': True}
        },
        'Expert+': {
            'ai_class': OptimizedMinimaxAI,
            'description': 'Godlike - Near perfect play 🔥',
            'kwargs': {'depth': 5, 'time_limit': 10.0, 'use_iterative_deepening': True}
        }
    }
    
    @staticmethod
    def get_ai(game, difficulty='Medium', player='O'):
        """
        Get AI instance for specified difficulty level
        
        Args:
            game: GomokuGame instance
            difficulty: Difficulty level ('Easy', 'Medium', 'Hard', 'Expert')
            player: AI player symbol (default 'O')
            
        Returns:
            AI instance
        """
        if difficulty not in AIManager.DIFFICULTIES:
            print(f"[Warning] Unknown difficulty '{difficulty}', using 'Medium'")
            difficulty = 'Medium'
        
        config = AIManager.DIFFICULTIES[difficulty]
        ai_class = config['ai_class']
        kwargs = config['kwargs'].copy()
        
        # Add player parameter if it's MinimaxAI
        if ai_class == MinimaxAI:
            kwargs['player'] = player
        
        return ai_class(game, **kwargs)
    
    @staticmethod
    def get_difficulty_list():
        """
        Get list of available difficulty levels
        
        Returns:
            List of difficulty names
        """
        return list(AIManager.DIFFICULTIES.keys())
    
    @staticmethod
    def get_description(difficulty):
        """
        Get description for a difficulty level
        
        Args:
            difficulty: Difficulty level name
            
        Returns:
            Description string
        """
        if difficulty in AIManager.DIFFICULTIES:
            return AIManager.DIFFICULTIES[difficulty]['description']
        return "Unknown difficulty"
