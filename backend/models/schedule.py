"""
ScheduleBlock Model
SQLAlchemy ORM model for schedule blocks.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class ScheduleBlock(Base):
    """
    ScheduleBlock model representing a time block in the schedule.

    Attributes:
        id: Primary key
        user_id: Owner user (for multi-user support)
        task_id: Associated task (if block_type is 'task')
        title: Block title/description
        start: Start hour (e.g., 9.5 for 9:30 AM)
        duration: Duration in hours
        block_type: 'fixed', 'focus', 'break', or 'task'
        created_at: Timestamp when block was created
        updated_at: Timestamp when block was last updated
    """
    __tablename__ = "schedule_blocks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    start = Column(Float, nullable=False)  # Hour of day
    duration = Column(Float, nullable=False)  # Hours
    block_type = Column(String(20), default="fixed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<ScheduleBlock(id={self.id}, title='{self.title}', start={self.start})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "userId": self.user_id,
            "taskId": self.task_id,
            "title": self.title,
            "start": self.start,
            "duration": self.duration,
            "type": self.block_type,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def end(self) -> float:
        """Calculate end hour."""
        return self.start + self.duration
