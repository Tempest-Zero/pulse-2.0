"""
MoodEntry Model
SQLAlchemy ORM model for mood tracking.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from .base import Base


# Valid mood values (matching frontend)
VALID_MOODS = {"calm", "energized", "focused", "tired", "happy", "stressed", "anxious", "sad", "excited", "overwhelmed", "exhausted", "neutral", "content", "okay"}


class MoodEntry(Base):
    """
    MoodEntry model representing a mood state at a point in time.
    
    Attributes:
        id: Primary key
        user_id: Owner user (for multi-user support)
        mood: One of the valid mood strings
        notes: Optional notes about the mood
        timestamp: When the mood was recorded
    """
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # nullable for migration
    mood = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self) -> str:
        return f"<MoodEntry(id={self.id}, mood='{self.mood}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "userId": self.user_id,
            "mood": self.mood,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @staticmethod
    def validate_mood(mood: str) -> bool:
        """Check if mood value is valid."""
        return mood.lower() in VALID_MOODS

