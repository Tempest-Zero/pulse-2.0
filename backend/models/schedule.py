"""
ScheduleBlock Model
SQLAlchemy ORM model for schedule blocks.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .base import Base


class ScheduleBlock(Base):
    """
    ScheduleBlock model representing a time block in the schedule.
    
    Attributes:
        id: Primary key
        title: Block title/description
        start: Start hour (e.g., 9.5 for 9:30 AM)
        duration: Duration in hours
        block_type: 'fixed', 'focus', 'break', or 'task'
        created_at: Timestamp when block was created
        updated_at: Timestamp when block was last updated
    """
    __tablename__ = "schedule_blocks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start = Column(Float, nullable=False)  # Hour of day
    duration = Column(Float, nullable=False)  # Hours
    block_type = Column(String(20), default="fixed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ScheduleBlock(id={self.id}, title='{self.title}', start={self.start})>"

    def to_dict(self):
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start,
            "duration": self.duration,
            "type": self.block_type,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def end(self):
        """Calculate end hour."""
        return self.start + self.duration
