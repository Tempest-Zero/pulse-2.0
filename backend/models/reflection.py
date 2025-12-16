"""
Reflection Model
SQLAlchemy ORM model for end-of-day reflections.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class Reflection(Base):
    """
    Reflection model representing an end-of-day reflection entry.

    Attributes:
        id: Primary key
        user_id: Owner user (for multi-user support)
        date: Date of the reflection
        mood_score: 1-5 scale (drained to energized)
        distractions: JSON array of distraction tag IDs
        note: Optional notes about the day
        completed_tasks: Number of tasks completed that day
        total_tasks: Total number of tasks that day
        created_at: Timestamp when reflection was created
    """
    __tablename__ = "reflections"
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    mood_score = Column(Integer, nullable=False)  # 1-5 scale
    distractions = Column(JSON, default=list)  # List of distraction tag IDs
    note = Column(Text, default="")
    completed_tasks = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Reflection(id={self.id}, date={self.date}, mood={self.mood_score})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "userId": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "moodScore": self.mood_score,
            "distractions": self.distractions or [],
            "note": self.note,
            "completedTasks": self.completed_tasks,
            "totalTasks": self.total_tasks,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def completion_rate(self) -> float:
        """Calculate task completion rate as percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100
