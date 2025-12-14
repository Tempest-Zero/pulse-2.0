"""
Task Schemas
Pydantic models for task API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255)
    duration: float = Field(default=1.0, ge=0.25, le=8.0)  # Hours
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, alias="durationMinutes")  # Minutes (frontend)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

    def get_duration_hours(self) -> float:
        """Get duration in hours, converting from minutes if provided."""
        if self.duration_minutes is not None:
            return self.duration_minutes / 60.0
        return self.duration

    class Config:
        populate_by_name = True


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    duration: Optional[float] = Field(None, ge=0.25, le=8.0)
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, alias="durationMinutes")
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    completed: Optional[bool] = None
    scheduled_at: Optional[float] = Field(None, ge=0, le=24)

    class Config:
        populate_by_name = True


class TaskResponse(BaseModel):
    """Schema for task responses."""
    id: int
    title: str
    name: Optional[str] = None  # Frontend alias
    duration: float
    duration_minutes: int = Field(alias="durationMinutes")  # Frontend format
    difficulty: str
    priority: str
    completed: bool
    done: Optional[bool] = None  # Frontend alias
    scheduled_at: Optional[float] = Field(None, alias="scheduledAt")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True

