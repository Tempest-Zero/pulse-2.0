"""
Task Schemas
Pydantic models for task API validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255)
    duration: Union[int, float] = Field(default=1.0, ge=0.25, le=8.0)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    
    @field_validator('duration')
    @classmethod
    def convert_duration_to_float(cls, v):
        """Convert duration to float (accepts both int and float)."""
        return float(v)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    duration: Optional[float] = Field(None, ge=0.25, le=8.0)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    completed: Optional[bool] = None
    scheduled_at: Optional[float] = Field(None, ge=0, le=24)


class TaskResponse(BaseModel):
    """Schema for task responses."""
    id: int
    title: str
    duration: float
    difficulty: str
    completed: bool
    scheduled_at: Optional[float] = Field(None, alias="scheduledAt")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
