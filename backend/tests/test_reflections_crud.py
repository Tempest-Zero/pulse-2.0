"""
Tests for reflections_crud module.
"""

import pytest
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from crud import reflections_crud


@pytest.fixture(autouse=True)
def clean_data():
    """Reset data file before and after each test."""
    data_file = reflections_crud.DATA_FILE
    
    if os.path.exists(data_file):
        os.remove(data_file)
    yield
    if os.path.exists(data_file):
        os.remove(data_file)


class TestSaveReflection:
    """Tests for save_reflection function."""
    
    def test_save_reflection_basic(self):
        """Should save a complete reflection entry."""
        reflection = reflections_crud.save_reflection(
            mood_score=4,
            distractions=["meetings", "notifications"],
            note="Pretty good day!",
            completed_tasks=5,
            total_tasks=7
        )
        
        assert reflection["id"] == 1
        assert reflection["moodScore"] == 4
        assert reflection["distractions"] == ["meetings", "notifications"]
        assert reflection["note"] == "Pretty good day!"
        assert reflection["completedTasks"] == 5
        assert reflection["totalTasks"] == 7
        assert reflection["date"] == date.today().isoformat()
    
    def test_save_reflection_empty_distractions(self):
        """Should work with no distractions."""
        reflection = reflections_crud.save_reflection(
            mood_score=5,
            distractions=[],
            note="",
            completed_tasks=10,
            total_tasks=10
        )
        
        assert reflection["distractions"] == []


class TestGetReflections:
    """Tests for get_reflections function."""
    
    def test_get_reflections_empty(self):
        """Should return empty list when no reflections."""
        reflections = reflections_crud.get_reflections()
        assert reflections == []
    
    def test_get_reflections_returns_all(self):
        """Should return all reflections."""
        reflections_crud.save_reflection(4, [], "", 5, 7)
        reflections_crud.save_reflection(3, ["fatigue"], "tired", 3, 7)
        
        reflections = reflections_crud.get_reflections()
        assert len(reflections) == 2
    
    def test_get_reflections_with_limit(self):
        """Should respect limit parameter."""
        for i in range(5):
            reflections_crud.save_reflection(i+1, [], "", i, 5)
        
        reflections = reflections_crud.get_reflections(limit=3)
        assert len(reflections) == 3


class TestGetReflectionById:
    """Tests for get_reflection_by_id function."""
    
    def test_get_existing_reflection(self):
        """Should return reflection when ID exists."""
        created = reflections_crud.save_reflection(4, [], "test", 5, 5)
        found = reflections_crud.get_reflection_by_id(created["id"])
        
        assert found is not None
        assert found["note"] == "test"
    
    def test_get_nonexistent_reflection(self):
        """Should return None for invalid ID."""
        result = reflections_crud.get_reflection_by_id(999)
        assert result is None


class TestGetReflectionByDate:
    """Tests for get_reflection_by_date function."""
    
    def test_get_reflection_by_date(self):
        """Should find reflection for specific date."""
        reflections_crud.save_reflection(4, [], "today", 5, 5)
        
        today = date.today().isoformat()
        found = reflections_crud.get_reflection_by_date(today)
        
        assert found is not None
        assert found["note"] == "today"
    
    def test_get_reflection_by_date_not_found(self):
        """Should return None when no reflection for date."""
        result = reflections_crud.get_reflection_by_date("2020-01-01")
        assert result is None


class TestUpdateReflection:
    """Tests for update_reflection function."""
    
    def test_update_mood_score(self):
        """Should update mood score."""
        reflection = reflections_crud.save_reflection(3, [], "", 5, 5)
        updated = reflections_crud.update_reflection(
            reflection["id"], 
            moodScore=5
        )
        
        assert updated["moodScore"] == 5
    
    def test_update_note(self):
        """Should update note."""
        reflection = reflections_crud.save_reflection(3, [], "old", 5, 5)
        updated = reflections_crud.update_reflection(
            reflection["id"], 
            note="new note"
        )
        
        assert updated["note"] == "new note"


class TestDeleteReflection:
    """Tests for delete_reflection function."""
    
    def test_delete_existing_reflection(self):
        """Should delete reflection and return True."""
        reflection = reflections_crud.save_reflection(4, [], "", 5, 5)
        result = reflections_crud.delete_reflection(reflection["id"])
        
        assert result == True
        assert reflections_crud.get_reflection_by_id(reflection["id"]) is None
    
    def test_delete_nonexistent_returns_false(self):
        """Should return False for invalid ID."""
        result = reflections_crud.delete_reflection(999)
        assert result == False


class TestAnalytics:
    """Tests for analytics functions."""
    
    def test_get_mood_average(self):
        """Should calculate average mood score."""
        reflections_crud.save_reflection(3, [], "", 5, 5)
        reflections_crud.save_reflection(4, [], "", 5, 5)
        reflections_crud.save_reflection(5, [], "", 5, 5)
        
        avg = reflections_crud.get_mood_average(days=7)
        assert avg == 4.0  # (3+4+5)/3
    
    def test_get_mood_average_no_data(self):
        """Should return None when no reflections."""
        avg = reflections_crud.get_mood_average()
        assert avg is None
    
    def test_get_common_distractions(self):
        """Should find most common distractions."""
        reflections_crud.save_reflection(3, ["meetings", "fatigue"], "", 5, 5)
        reflections_crud.save_reflection(4, ["meetings"], "", 5, 5)
        reflections_crud.save_reflection(4, ["notifications", "meetings"], "", 5, 5)
        
        common = reflections_crud.get_common_distractions()
        
        # meetings should be most common (3 times)
        assert common[0] == ("meetings", 3)
