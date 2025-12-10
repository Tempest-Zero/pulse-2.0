"""
Tests for mood_crud module.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from crud import mood_crud


@pytest.fixture(autouse=True)
def clean_data():
    """Reset data file before and after each test."""
    data_file = mood_crud.DATA_FILE
    
    if os.path.exists(data_file):
        os.remove(data_file)
    yield
    if os.path.exists(data_file):
        os.remove(data_file)


class TestSetMood:
    """Tests for set_mood function."""
    
    def test_set_valid_mood(self):
        """Should set a valid mood and return entry."""
        entry = mood_crud.set_mood("focused")
        
        assert entry["id"] == 1
        assert entry["mood"] == "focused"
        assert "timestamp" in entry
    
    def test_set_all_valid_moods(self):
        """Should accept all valid mood values."""
        valid_moods = ["calm", "energized", "focused", "tired"]
        
        for mood in valid_moods:
            entry = mood_crud.set_mood(mood)
            assert entry["mood"] == mood
    
    def test_set_invalid_mood_raises_error(self):
        """Should raise ValueError for invalid mood."""
        with pytest.raises(ValueError):
            mood_crud.set_mood("invalid_mood")


class TestGetCurrentMood:
    """Tests for get_current_mood function."""
    
    def test_get_default_mood(self):
        """Should return 'calm' as default."""
        mood = mood_crud.get_current_mood()
        assert mood == "calm"
    
    def test_get_current_mood_after_set(self):
        """Should return most recently set mood."""
        mood_crud.set_mood("energized")
        mood_crud.set_mood("tired")
        
        current = mood_crud.get_current_mood()
        assert current == "tired"


class TestGetMoodHistory:
    """Tests for get_mood_history function."""
    
    def test_get_history_empty(self):
        """Should return empty list when no history."""
        history = mood_crud.get_mood_history()
        assert history == []
    
    def test_get_history_returns_all(self):
        """Should return all mood entries."""
        mood_crud.set_mood("calm")
        mood_crud.set_mood("focused")
        mood_crud.set_mood("tired")
        
        history = mood_crud.get_mood_history()
        assert len(history) == 3
    
    def test_get_history_most_recent_first(self):
        """Should return most recent entries first."""
        mood_crud.set_mood("calm")
        mood_crud.set_mood("focused")
        mood_crud.set_mood("tired")
        
        history = mood_crud.get_mood_history()
        assert history[0]["mood"] == "tired"
    
    def test_get_history_with_limit(self):
        """Should respect limit parameter."""
        for _ in range(10):
            mood_crud.set_mood("calm")
        
        history = mood_crud.get_mood_history(limit=5)
        assert len(history) == 5


class TestGetMoodById:
    """Tests for get_mood_by_id function."""
    
    def test_get_existing_entry(self):
        """Should return entry when ID exists."""
        created = mood_crud.set_mood("focused")
        found = mood_crud.get_mood_by_id(created["id"])
        
        assert found is not None
        assert found["mood"] == "focused"
    
    def test_get_nonexistent_entry(self):
        """Should return None for invalid ID."""
        result = mood_crud.get_mood_by_id(999)
        assert result is None


class TestDeleteMoodEntry:
    """Tests for delete_mood_entry function."""
    
    def test_delete_existing_entry(self):
        """Should delete entry and return True."""
        entry = mood_crud.set_mood("focused")
        result = mood_crud.delete_mood_entry(entry["id"])
        
        assert result == True
        assert mood_crud.get_mood_by_id(entry["id"]) is None
    
    def test_delete_nonexistent_returns_false(self):
        """Should return False for invalid ID."""
        result = mood_crud.delete_mood_entry(999)
        assert result == False


class TestMoodCounts:
    """Tests for get_mood_counts function."""
    
    def test_get_mood_counts(self):
        """Should count occurrences of each mood."""
        mood_crud.set_mood("calm")
        mood_crud.set_mood("calm")
        mood_crud.set_mood("focused")
        mood_crud.set_mood("tired")
        
        counts = mood_crud.get_mood_counts()
        
        assert counts["calm"] == 2
        assert counts["focused"] == 1
        assert counts["tired"] == 1
        assert counts["energized"] == 0
    
    def test_get_mood_counts_empty(self):
        """Should return zeros when no history."""
        counts = mood_crud.get_mood_counts()
        
        assert all(count == 0 for count in counts.values())


class TestGetMostCommonMood:
    """Tests for get_most_common_mood function."""
    
    def test_get_most_common_mood(self):
        """Should return most frequent mood."""
        mood_crud.set_mood("calm")
        mood_crud.set_mood("focused")
        mood_crud.set_mood("focused")
        mood_crud.set_mood("focused")
        
        most_common = mood_crud.get_most_common_mood()
        assert most_common == "focused"
    
    def test_get_most_common_mood_no_history(self):
        """Should return None when no history."""
        result = mood_crud.get_most_common_mood()
        assert result is None


class TestClearHistory:
    """Tests for clear_history function."""
    
    def test_clear_history(self):
        """Should remove all history and return count."""
        mood_crud.set_mood("calm")
        mood_crud.set_mood("focused")
        mood_crud.set_mood("tired")
        
        count = mood_crud.clear_history()
        
        assert count == 3
        assert mood_crud.get_mood_history() == []
    
    def test_clear_history_keeps_current(self):
        """Should keep current mood after clearing."""
        mood_crud.set_mood("energized")
        mood_crud.clear_history()
        
        current = mood_crud.get_current_mood()
        assert current == "energized"
