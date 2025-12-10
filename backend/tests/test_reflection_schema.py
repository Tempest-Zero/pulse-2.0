"""
Tests for reflection schemas.
"""

import pytest
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pydantic import ValidationError
from schema.reflection import ReflectionCreate, ReflectionUpdate, ReflectionResponse


class TestReflectionCreate:
    """Tests for ReflectionCreate schema."""
    
    def test_valid_reflection_minimal(self):
        """Should create reflection with required fields."""
        reflection = ReflectionCreate(
            moodScore=4,
            completedTasks=5,
            totalTasks=7
        )
        
        assert reflection.mood_score == 4
        assert reflection.completed_tasks == 5
        assert reflection.total_tasks == 7
        assert reflection.distractions == []
        assert reflection.note == ""
    
    def test_valid_reflection_all_fields(self):
        """Should create reflection with all fields."""
        reflection = ReflectionCreate(
            moodScore=3,
            distractions=["meetings", "fatigue"],
            note="Tough day but got through it",
            completedTasks=3,
            totalTasks=5
        )
        
        assert reflection.distractions == ["meetings", "fatigue"]
        assert reflection.note == "Tough day but got through it"
    
    def test_invalid_mood_score_too_low(self):
        """Should reject mood score less than 1."""
        with pytest.raises(ValidationError):
            ReflectionCreate(moodScore=0, completedTasks=5, totalTasks=5)
    
    def test_invalid_mood_score_too_high(self):
        """Should reject mood score greater than 5."""
        with pytest.raises(ValidationError):
            ReflectionCreate(moodScore=6, completedTasks=5, totalTasks=5)
    
    def test_valid_mood_scores(self):
        """Should accept all valid mood scores."""
        for score in [1, 2, 3, 4, 5]:
            reflection = ReflectionCreate(
                moodScore=score,
                completedTasks=5,
                totalTasks=5
            )
            assert reflection.mood_score == score
    
    def test_invalid_negative_tasks(self):
        """Should reject negative task counts."""
        with pytest.raises(ValidationError):
            ReflectionCreate(moodScore=3, completedTasks=-1, totalTasks=5)


class TestReflectionUpdate:
    """Tests for ReflectionUpdate schema."""
    
    def test_all_fields_optional(self):
        """Should allow empty update."""
        update = ReflectionUpdate()
        
        assert update.mood_score is None
        assert update.distractions is None
        assert update.note is None
    
    def test_partial_update(self):
        """Should allow partial updates."""
        update = ReflectionUpdate(moodScore=5, note="Changed my mind")
        
        assert update.mood_score == 5
        assert update.note == "Changed my mind"


class TestReflectionResponse:
    """Tests for ReflectionResponse schema."""
    
    def test_response_from_dict(self):
        """Should create response from dict."""
        data = {
            "id": 1,
            "date": date.today(),
            "moodScore": 4,
            "distractions": ["meetings"],
            "note": "Good day",
            "completedTasks": 5,
            "totalTasks": 7,
            "createdAt": None,
        }
        response = ReflectionResponse(**data)
        
        assert response.id == 1
        assert response.mood_score == 4
        assert response.completed_tasks == 5
