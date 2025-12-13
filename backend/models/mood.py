"""
MoodEntry Model
SQLAlchemy ORM model for mood tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base


# Valid mood values (expanded for frontend compatibility)
# Original: calm, energized, focused, tired
# Frontend uses: energized, good, neutral, low, exhausted
VALID_MOODS = {"calm", "energized", "focused", "tired", "good", "neutral", "low", "exhausted"}


class MoodEntry(Base):
    """
    MoodEntry model representing a mood state at a point in time.
    
    Attributes:
        id: Primary key
        mood: One of 'calm', 'energized', 'focused', 'tired'
        timestamp: When the mood was recorded
    """
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    mood = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<MoodEntry(id={self.id}, mood='{self.mood}')>"

    def to_dict(self):
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "mood": self.mood,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @staticmethod
    def validate_mood(mood: str) -> bool:
        """Check if mood value is valid."""
        return mood in VALID_MOODS
