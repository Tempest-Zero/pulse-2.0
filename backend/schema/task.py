"""
Task Schemas
Pydantic models for task API validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Union
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    duration: Union[int, float] = Field(default=1.0, ge=0.25, le=8.0)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    parent_id: Optional[int] = Field(None, description="Parent task ID for subtasks")
    
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
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    description: Optional[str] = None
    duration: float
    difficulty: str
    completed: bool
    scheduled_at: Optional[float] = Field(None, alias="scheduledAt")
    parent_id: Optional[int] = Field(None, alias="parentId")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
