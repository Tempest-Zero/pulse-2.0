"""
Task Model
SQLAlchemy ORM model for tasks.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base


class Task(Base):
    """
    Task model representing a todo item.
    
    Attributes:
        id: Primary key
        title: Task title/description
        duration: Estimated duration in hours
        difficulty: 'easy', 'medium', or 'hard'
        completed: Whether the task is done
        scheduled_at: Hour when task is scheduled (e.g., 9.5 for 9:30 AM)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    duration = Column(Float, default=1.0)
    difficulty = Column(String(20), default="medium")
    completed = Column(Boolean, default=False)
    scheduled_at = Column(Float, nullable=True)  # Hour of day (e.g., 9.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"

    def to_dict(self):
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration,
            "difficulty": self.difficulty,
            "completed": self.completed,
            "scheduledAt": self.scheduled_at,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
