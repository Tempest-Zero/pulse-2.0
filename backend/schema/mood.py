"""
Mood Schemas
Pydantic models for mood API validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# Valid mood values (expanded for frontend compatibility)
VALID_MOODS = {"calm", "energized", "focused", "tired", "good", "neutral", "low", "exhausted"}


class MoodCreate(BaseModel):
    """Schema for setting the current mood."""
    mood: str

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, v: str) -> str:
        if v not in VALID_MOODS:
            raise ValueError(f"Invalid mood. Must be one of: {', '.join(VALID_MOODS)}")
        return v


class MoodResponse(BaseModel):
    """Schema for mood entry responses."""
    id: int
    mood: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
