"""
RecommendationLog Model
SQLAlchemy ORM model for tracking AI recommendations.
"""

from typing import Any, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from .base import Base


class RecommendationLog(Base):
    """
    Log of AI recommendations for tracking and learning.
    
    Stores:
    - State snapshot at recommendation time
    - Action recommended
    - Strategy used (rule/rl/hybrid)
    - Outcome and reward (for learning)
    - Tracking fields for implicit feedback inference
    """
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # State at recommendation time
    state_snapshot = Column(JSON, nullable=True)  # Full state for debugging
    state_key = Column(String(100), nullable=False, index=True)  # "morning|monday|high|low"
    
    # Recommendation details
    action_type = Column(String(50), nullable=False, index=True)
    suggested_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    suggested_duration_minutes = Column(Integer, nullable=True)
    
    # Strategy and confidence
    confidence = Column(Float, nullable=False, default=0.0)
    strategy_used = Column(String(20), nullable=False)  # rule, rl, hybrid
    explanation = Column(Text, nullable=True)
    
    # Outcome tracking
    outcome = Column(String(50), nullable=True, index=True)  # completed, partial, skipped, ignored
    reward = Column(Float, nullable=True)
    was_followed = Column(Boolean, default=False)
    
    # Mood tracking
    mood_before = Column(String(20), nullable=True)
    mood_after = Column(String(20), nullable=True)
    
    # User feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Timestamps for outcome
    outcome_recorded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Implicit feedback tracking
    next_recommendation_at = Column(DateTime(timezone=True), nullable=True)
    task_completed_at = Column(DateTime(timezone=True), nullable=True)
    activity_gap_seconds = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<RecommendationLog(id={self.id}, action={self.action_type}, outcome={self.outcome})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "userId": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "stateKey": self.state_key,
            "actionType": self.action_type,
            "suggestedTaskId": self.suggested_task_id,
            "suggestedDurationMinutes": self.suggested_duration_minutes,
            "confidence": self.confidence,
            "strategyUsed": self.strategy_used,
            "explanation": self.explanation,
            "outcome": self.outcome,
            "reward": self.reward,
            "wasFollowed": self.was_followed,
            "moodBefore": self.mood_before,
            "moodAfter": self.mood_after,
            "userRating": self.user_rating,
            "outcomeRecordedAt": self.outcome_recorded_at.isoformat() if self.outcome_recorded_at else None,
        }
