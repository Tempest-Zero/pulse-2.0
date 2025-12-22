"""
Feedback Model
SQLAlchemy ORM model for user feedback and ratings.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Feedback(Base):
    """
    Feedback model for storing user ratings and reviews.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        rating: Rating from 1-5 stars
        category: Category of feedback (general, feature, bug, improvement)
        review: User's written review/feedback
        created_at: When the feedback was submitted
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    category = Column(String(50), default="general")  # general, feature, bug, improvement
    review = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, user_id={self.user_id}, rating={self.rating})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "userId": self.user_id,
            "rating": self.rating,
            "category": self.category,
            "review": self.review,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
