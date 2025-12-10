"""
Tests for mood schemas.
"""

import pytest
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pydantic import ValidationError
from schema.mood import MoodCreate, MoodResponse, VALID_MOODS


class TestMoodCreate:
    """Tests for MoodCreate schema."""
    
    def test_valid_mood_calm(self):
        """Should create mood entry for calm."""
        mood = MoodCreate(mood="calm")
        assert mood.mood == "calm"
    
    def test_valid_mood_energized(self):
        """Should create mood entry for energized."""
        mood = MoodCreate(mood="energized")
        assert mood.mood == "energized"
    
    def test_valid_mood_focused(self):
        """Should create mood entry for focused."""
        mood = MoodCreate(mood="focused")
        assert mood.mood == "focused"
    
    def test_valid_mood_tired(self):
        """Should create mood entry for tired."""
        mood = MoodCreate(mood="tired")
        assert mood.mood == "tired"
    
    def test_all_valid_moods(self):
        """Should accept all valid mood values."""
        for valid_mood in VALID_MOODS:
            mood = MoodCreate(mood=valid_mood)
            assert mood.mood == valid_mood
    
    def test_invalid_mood(self):
        """Should reject invalid mood value."""
        with pytest.raises(ValidationError) as exc_info:
            MoodCreate(mood="happy")
        
        assert "Invalid mood" in str(exc_info.value)
    
    def test_invalid_mood_empty(self):
        """Should reject empty mood."""
        with pytest.raises(ValidationError):
            MoodCreate(mood="")
    
    def test_invalid_mood_case_sensitive(self):
        """Should reject wrong case (case sensitive)."""
        with pytest.raises(ValidationError):
            MoodCreate(mood="CALM")
        
        with pytest.raises(ValidationError):
            MoodCreate(mood="Focused")


class TestMoodResponse:
    """Tests for MoodResponse schema."""
    
    def test_response_from_dict(self):
        """Should create response from dict."""
        data = {
            "id": 1,
            "mood": "focused",
            "timestamp": datetime.now(),
        }
        response = MoodResponse(**data)
        
        assert response.id == 1
        assert response.mood == "focused"
        assert response.timestamp is not None
    
    def test_response_optional_timestamp(self):
        """Should allow None timestamp."""
        data = {
            "id": 1,
            "mood": "calm",
            "timestamp": None,
        }
        response = MoodResponse(**data)
        
        assert response.timestamp is None
