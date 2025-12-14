"""
Schedule Block Schemas
Pydantic models for schedule block API validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ScheduleBlockCreate(BaseModel):
    """Schema for creating a new schedule block."""
    title: str = Field(..., min_length=1, max_length=255)
    start: float = Field(..., ge=0, le=24)
    duration: float = Field(..., ge=0.25, le=8.0)
    block_type: str = Field(default="fixed", pattern="^(fixed|focus|break|task)$")


class ScheduleBlockUpdate(BaseModel):
    """Schema for updating an existing schedule block."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    start: Optional[float] = Field(None, ge=0, le=24)
    duration: Optional[float] = Field(None, ge=0.25, le=8.0)
    block_type: Optional[str] = Field(None, pattern="^(fixed|focus|break|task)$")


class ScheduleBlockResponse(BaseModel):
    """Schema for schedule block responses."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    start: float
    duration: float
    block_type: str = Field(alias="type")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
