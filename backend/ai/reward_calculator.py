"""
Reward Calculator
Computes calibrated rewards for Q-Learning updates.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Session

from .mood_mapper import MoodMapper


class Outcome(str, Enum):
    """Possible outcomes of a recommendation."""
    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    IGNORED = "ignored"


@dataclass
class RewardWeights:
    """Calibrated reward weights (v2.0)."""
    # Base outcomes
    task_completed: float = 1.0
    task_partial: float = 0.3    # Reduced from 0.4
    task_skipped: float = -0.5   # Increased penalty from -0.3
    task_ignored: float = -0.2
    
    # Mood changes
    mood_improved: float = 0.2   # Reduced from 0.3
    mood_declined: float = -0.3  # Increased penalty from -0.2
    
    # Bonuses
    rating_bonus_high: float = 0.5  # 4-5 star rating (increased from 0.25)
    rating_bonus_mid: float = 0.1   # 3 star rating
    time_bonus: float = 0.2         # Completed within suggested duration
    
    # Recency decay
    recency_decay_factor: float = 0.95  # Per-day decay


WEIGHTS = RewardWeights()


class RewardCalculator:
    """
    Calculate rewards for Q-Learning updates.
    
    Reward range: [-0.8, 2.0]
    Formula: base_outcome + mood_delta + time_bonus + rating_bonus * recency_weight
    """
    
    def calculate_reward(
        self,
        outcome: Outcome,
        mood_before: Optional[str] = None,
        mood_after: Optional[str] = None,
        user_rating: Optional[int] = None,
        suggested_duration_minutes: Optional[int] = None,
        actual_duration_minutes: Optional[int] = None,
        days_old: int = 0
    ) -> float:
        """
        Calculate total reward for a recommendation outcome.
        
        Args:
            outcome: The outcome of the recommendation
            mood_before: Mood string before the activity
            mood_after: Mood string after the activity
            user_rating: User's explicit rating (1-5)
            suggested_duration_minutes: Suggested duration for the action
            actual_duration_minutes: Actual time spent
            days_old: How many days old this interaction is (for recency decay)
            
        Returns:
            Reward value in range [-0.8, 2.0]
        """
        # Base outcome reward
        base_reward = self._get_base_reward(outcome)
        
        # Mood change bonus/penalty
        mood_delta = self._calculate_mood_delta(mood_before, mood_after)
        
        # Time bonus
        time_bonus = self._calculate_time_bonus(
            suggested_duration_minutes, 
            actual_duration_minutes
        )
        
        # Rating bonus
        rating_bonus = self._calculate_rating_bonus(user_rating)
        
        # Sum up components
        total_reward = base_reward + mood_delta + time_bonus + rating_bonus
        
        # Apply recency decay
        recency_weight = self._apply_recency_decay(days_old)
        total_reward *= recency_weight
        
        # Clamp to expected range
        return max(-0.8, min(2.0, total_reward))
    
    def _get_base_reward(self, outcome: Outcome) -> float:
        """Get base reward for an outcome."""
        if outcome == Outcome.COMPLETED:
            return WEIGHTS.task_completed
        elif outcome == Outcome.PARTIAL:
            return WEIGHTS.task_partial
        elif outcome == Outcome.SKIPPED:
            return WEIGHTS.task_skipped
        elif outcome == Outcome.IGNORED:
            return WEIGHTS.task_ignored
        return 0.0
    
    def _calculate_mood_delta(
        self, 
        mood_before: Optional[str], 
        mood_after: Optional[str]
    ) -> float:
        """
        Calculate reward modifier based on mood change.
        
        Returns positive value if mood improved, negative if declined.
        """
        if mood_before is None or mood_after is None:
            return 0.0
        
        score_before = MoodMapper.get_score(mood_before)
        score_after = MoodMapper.get_score(mood_after)
        
        delta = score_after - score_before
        
        if delta > 0:
            # Mood improved
            return WEIGHTS.mood_improved
        elif delta < 0:
            # Mood declined
            return WEIGHTS.mood_declined
        else:
            return 0.0
    
    def _calculate_time_bonus(
        self,
        suggested_duration: Optional[int],
        actual_duration: Optional[int]
    ) -> float:
        """
        Calculate bonus for completing within suggested time.
        
        Bonus if actual <= suggested * 1.2 (20% buffer)
        """
        if suggested_duration is None or actual_duration is None:
            return 0.0
        
        if suggested_duration <= 0:
            return 0.0
        
        # Allow 20% buffer
        if actual_duration <= suggested_duration * 1.2:
            return WEIGHTS.time_bonus
        
        return 0.0
    
    def _calculate_rating_bonus(self, rating: Optional[int]) -> float:
        """Calculate bonus based on user rating (1-5)."""
        if rating is None:
            return 0.0
        
        if rating >= 4:
            return WEIGHTS.rating_bonus_high
        elif rating == 3:
            return WEIGHTS.rating_bonus_mid
        else:
            return 0.0  # No bonus for low ratings
    
    def _apply_recency_decay(self, days_old: int) -> float:
        """
        Apply recency decay to weight recent interactions higher.
        
        Returns decay factor: 0.95 ^ days_old
        """
        if days_old <= 0:
            return 1.0
        return WEIGHTS.recency_decay_factor ** days_old


def calculate_reward_simple(outcome: Outcome) -> float:
    """
    Simplified reward calculation using only outcome.
    
    Useful for quick updates without full context.
    """
    calculator = RewardCalculator()
    return calculator.calculate_reward(outcome)
