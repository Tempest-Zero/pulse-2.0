"""
Mood Schemas
Pydantic models for mood API validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


# Valid mood values
VALID_MOODS = {"calm", "energized", "focused", "tired"}


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    mood: str
    timestamp: Optional[datetime] = None
