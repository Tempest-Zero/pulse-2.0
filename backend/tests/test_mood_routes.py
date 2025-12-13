"""
Tests for mood API routes.
"""

import pytest
from fastapi import status


class TestMoodRoutes:
    """Test cases for mood routes."""
    
    def test_get_current_mood_default(self, client):
        """Test getting current mood when no history exists."""
        response = client.get("/mood/current")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["mood"] == "calm"  # Default mood
        assert data["timestamp"] is None
    
    def test_set_mood(self, client):
        """Test setting a new mood."""
        mood_data = {"mood": "focused"}
        response = client.post("/mood", json=mood_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["mood"] == "focused"
        assert "id" in data
        assert "timestamp" in data
    
    def test_get_current_mood_after_set(self, client, test_mood_entry):
        """Test getting current mood after setting one."""
        response = client.get("/mood/current")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["mood"] == "focused"
        assert data["timestamp"] is not None
    
    def test_get_mood_history_empty(self, client):
        """Test getting mood history when empty."""
        response = client.get("/mood/history")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_mood_history_with_data(self, client, test_mood_entry):
        """Test getting mood history with data."""
        response = client.get("/mood/history")
        assert response.status_code == status.HTTP_200_OK
        
        history = response.json()
        assert len(history) >= 1
        assert history[0]["mood"] == "focused"
    
    def test_get_mood_history_with_limit(self, client, db_session):
        """Test getting mood history with limit."""
        from models.mood import MoodEntry
        
        # Create multiple mood entries
        moods = ["calm", "energized", "focused", "tired", "calm"]
        for mood in moods:
            entry = MoodEntry(mood=mood)
            db_session.add(entry)
        db_session.commit()
        
        response = client.get("/mood/history?limit=3")
        assert response.status_code == status.HTTP_200_OK
        
        history = response.json()
        assert len(history) == 3
    
    def test_get_mood_counts(self, client, db_session):
        """Test getting mood counts."""
        from models.mood import MoodEntry
        
        # Create mood entries
        moods = ["calm", "calm", "focused", "tired"]
        for mood in moods:
            entry = MoodEntry(mood=mood)
            db_session.add(entry)
        db_session.commit()
        
        response = client.get("/mood/analytics/counts")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "counts" in data
        assert data["counts"]["calm"] == 2
        assert data["counts"]["focused"] == 1
        assert data["counts"]["tired"] == 1
        assert data["counts"]["energized"] == 0
    
    def test_get_most_common_mood(self, client, db_session):
        """Test getting most common mood."""
        from models.mood import MoodEntry
        
        # Create mood entries with one being most common
        moods = ["focused", "focused", "focused", "calm", "tired"]
        for mood in moods:
            entry = MoodEntry(mood=mood)
            db_session.add(entry)
        db_session.commit()
        
        response = client.get("/mood/analytics/most-common")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["most_common"] == "focused"
        assert data["count"] == 3
    
    def test_get_most_common_mood_empty(self, client):
        """Test getting most common mood when no history."""
        response = client.get("/mood/analytics/most-common")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["most_common"] is None
        assert data["count"] == 0
    
    def test_get_mood_entry_by_id(self, client, test_mood_entry):
        """Test getting a single mood entry by ID."""
        response = client.get(f"/mood/{test_mood_entry.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_mood_entry.id
        assert data["mood"] == "focused"
    
    def test_get_mood_entry_not_found(self, client):
        """Test getting a non-existent mood entry."""
        response = client.get("/mood/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_mood_entry(self, client, test_mood_entry):
        """Test deleting a mood entry."""
        response = client.delete(f"/mood/{test_mood_entry.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify entry is deleted
        get_response = client.get(f"/mood/{test_mood_entry.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_clear_mood_history(self, client, test_mood_entry):
        """Test clearing all mood history."""
        response = client.delete("/mood/history/clear")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify history is empty
        get_response = client.get("/mood/history")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json() == []
    
    def test_set_all_valid_moods(self, client):
        """Test setting all valid mood values."""
        valid_moods = ["calm", "energized", "focused", "tired"]
        
        for mood in valid_moods:
            response = client.post("/mood", json={"mood": mood})
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["mood"] == mood
