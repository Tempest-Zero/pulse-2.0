"""
Reflection Schemas
Pydantic models for reflection API validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date


class ReflectionCreate(BaseModel):
    """Schema for creating a new reflection."""
    model_config = ConfigDict(populate_by_name=True)

    mood_score: int = Field(..., ge=1, le=5, alias="moodScore")
    distractions: List[str] = Field(default_factory=list)
    note: str = Field(default="", max_length=1000)
    completed_tasks: int = Field(..., ge=0, alias="completedTasks")
    total_tasks: int = Field(..., ge=0, alias="totalTasks")


class ReflectionUpdate(BaseModel):
    """Schema for updating an existing reflection."""
    model_config = ConfigDict(populate_by_name=True)

    mood_score: Optional[int] = Field(None, ge=1, le=5, alias="moodScore")
    distractions: Optional[List[str]] = None
    note: Optional[str] = Field(None, max_length=1000)


class ReflectionResponse(BaseModel):
    """Schema for reflection responses."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    date: date
    mood_score: int = Field(alias="moodScore")
    distractions: List[str]
    note: str
    completed_tasks: int = Field(alias="completedTasks")
    total_tasks: int = Field(alias="totalTasks")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
