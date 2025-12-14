"""
User Model
SQLAlchemy ORM model for users.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """
    User model for multi-user support.
    
    Attributes:
        id: Primary key
        username: Unique username
        created_at: When the user was created
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships will be added when task/mood models are updated
    # tasks = relationship("Task", back_populates="user")
    # mood_entries = relationship("MoodEntry", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
