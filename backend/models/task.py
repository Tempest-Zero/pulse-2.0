"""
Task Model
SQLAlchemy ORM model for tasks.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from .base import Base


class Task(Base):
    """
    Task model representing a todo item.
    
    Attributes:
        id: Primary key
        user_id: Owner user (for multi-user support)
        title: Task title/description
        description: Detailed task description
        duration: Estimated duration in hours (legacy)
        estimated_duration: Estimated duration in minutes (AI)
        difficulty: 'easy', 'medium', or 'hard'
        priority: 1-5 scale (1=lowest, 5=highest) for AI
        deadline: When task is due (for urgency calculation)
        status: 'pending', 'in_progress', 'completed'
        completed: Whether the task is done (legacy compatibility)
        completed_at: When the task was completed
        scheduled_at: Hour when task is scheduled (e.g., 9.5 for 9:30 AM)
        is_deleted: Soft delete flag (critical for AI queries)
        is_archived: Archive flag for completed tasks
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # nullable for migration
    parent_id = Column(Integer, ForeignKey('tasks.id'), nullable=True, index=True)  # For subtasks
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Float, default=1.0)  # Legacy: hours
    estimated_duration = Column(Integer, nullable=True)  # Minutes for AI
    difficulty = Column(String(20), default="medium")
    priority = Column(Integer, default=3, nullable=False)  # 1-5 scale for AI
    deadline = Column(DateTime(timezone=True), nullable=True, index=True)
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    completed = Column(Boolean, default=False)  # Legacy compatibility
    completed_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(Float, nullable=True)  # Hour of day (e.g., 9.5)
    is_deleted = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite index for AI queries
    __table_args__ = (
        Index('ix_tasks_user_status_deleted', 'user_id', 'status', 'is_deleted'),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status={self.status})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (for API responses)."""
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "estimatedDuration": self.estimated_duration,
            "difficulty": self.difficulty,
            "priority": self.priority,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "status": self.status,
            "completed": self.completed,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "scheduledAt": self.scheduled_at,
            "parentId": self.parent_id,
            "isDeleted": self.is_deleted,
            "isArchived": self.is_archived,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

