"""
Mood Mapper
Maps string moods to numeric scores for energy calculation.
"""

from typing import Dict


class MoodMapper:
    """Map string moods to numeric scores for energy calculation."""
    
    MOOD_SCORES: Dict[str, int] = {
        # High energy (8-10)
        "energized": 9,
        "focused": 8,
        "happy": 8,
        "excited": 9,
        
        # Medium energy (5-7)
        "calm": 6,
        "content": 7,
        "neutral": 5,
        "okay": 5,
        
        # Low energy (1-4)
        "tired": 3,
        "stressed": 4,
        "anxious": 4,
        "sad": 2,
        "overwhelmed": 2,
        "exhausted": 1,
    }
    
    # Default score when mood is unknown
    DEFAULT_SCORE: int = 5
    
    @classmethod
    def get_score(cls, mood: str | None) -> int:
        """
        Convert mood string to numeric score (1-10).
        
        Args:
            mood: Mood string (e.g., 'energized', 'tired')
            
        Returns:
            Numeric score 1-10
        """
        if mood is None:
            return cls.DEFAULT_SCORE
        mood_lower = mood.lower().strip()
        return cls.MOOD_SCORES.get(mood_lower, cls.DEFAULT_SCORE)
    
    @classmethod
    def get_energy_category(cls, mood: str | None) -> str:
        """
        Get energy level category from mood.
        
        Args:
            mood: Mood string
            
        Returns:
            'high', 'medium', or 'low'
        """
        score = cls.get_score(mood)
        if score >= 8:
            return "high"
        elif score >= 5:
            return "medium"
        else:
            return "low"
    
    @classmethod
    def is_valid_mood(cls, mood: str) -> bool:
        """Check if a mood string is recognized."""
        return mood.lower().strip() in cls.MOOD_SCORES
