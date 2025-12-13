"""
Tests for reflections API routes.
"""

import pytest
from fastapi import status
from datetime import date, timedelta


class TestReflectionsRoutes:
    """Test cases for reflections routes."""
    
    def test_get_reflections_empty(self, client):
        """Test getting all reflections when database is empty."""
        response = client.get("/reflections")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_reflection(self, client):
        """Test creating a new reflection."""
        reflection_data = {
            "moodScore": 4,
            "distractions": ["phone", "meetings"],
            "note": "Productive day overall",
            "completedTasks": 7,
            "totalTasks": 10
        }
        response = client.post("/reflections", json=reflection_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["moodScore"] == 4
        assert data["distractions"] == ["phone", "meetings"]
        assert data["note"] == "Productive day overall"
        assert data["completedTasks"] == 7
        assert data["totalTasks"] == 10
        assert "id" in data
        assert "date" in data
    
    def test_create_reflection_duplicate_today(self, client, test_reflection):
        """Test creating duplicate reflection for today fails."""
        reflection_data = {
            "moodScore": 3,
            "distractions": [],
            "note": "Another note",
            "completedTasks": 0,
            "totalTasks": 0
        }
        response = client.post("/reflections", json=reflection_data)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()
    
    def test_get_reflections_with_data(self, client, test_reflection):
        """Test getting all reflections with data."""
        response = client.get("/reflections")
        assert response.status_code == status.HTTP_200_OK
        
        reflections = response.json()
        assert len(reflections) >= 1
    
    def test_get_today_reflection(self, client, test_reflection):
        """Test getting today's reflection."""
        response = client.get("/reflections/today")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_reflection.id
        assert data["date"] == date.today().isoformat()
    
    def test_get_today_reflection_not_found(self, client):
        """Test getting today's reflection when none exists."""
        response = client.get("/reflections/today")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_reflection_by_id(self, client, test_reflection):
        """Test getting a single reflection by ID."""
        response = client.get(f"/reflections/{test_reflection.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_reflection.id
    
    def test_get_reflection_not_found(self, client):
        """Test getting a non-existent reflection."""
        response = client.get("/reflections/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_reflection_by_date(self, client, test_reflection):
        """Test getting reflection for a specific date."""
        today = date.today().isoformat()
        response = client.get(f"/reflections/date/{today}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["date"] == today
    
    def test_get_reflection_by_date_not_found(self, client):
        """Test getting reflection for a date with no data."""
        old_date = (date.today() - timedelta(days=30)).isoformat()
        response = client.get(f"/reflections/date/{old_date}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_reflection(self, client, test_reflection):
        """Test updating a reflection."""
        update_data = {"moodScore": 5, "note": "Updated note"}
        response = client.patch(f"/reflections/{test_reflection.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["moodScore"] == 5
        assert data["note"] == "Updated note"
    
    def test_delete_reflection(self, client, test_reflection):
        """Test deleting a reflection."""
        response = client.delete(f"/reflections/{test_reflection.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify reflection is deleted
        get_response = client.get(f"/reflections/{test_reflection.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_mood_average(self, client, db_session):
        """Test getting average mood score."""
        from models.reflection import Reflection
        
        # Create reflections with different moods
        for i, score in enumerate([3, 4, 5, 4, 3]):
            reflection = Reflection(
                date=date.today() - timedelta(days=i+1),
                mood_score=score,
                distractions=[]
            )
            db_session.add(reflection)
        db_session.commit()
        
        response = client.get("/reflections/analytics/mood-average?days=7")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "average_mood" in data
        assert data["days"] == 7
    
    def test_get_common_distractions(self, client, db_session):
        """Test getting common distractions."""
        from models.reflection import Reflection
        
        # Create reflections with distractions
        distractions_list = [
            ["phone", "email"],
            ["phone", "meetings"],
            ["phone"],
        ]
        
        for i, distractions in enumerate(distractions_list):
            reflection = Reflection(
                date=date.today() - timedelta(days=i+1),
                mood_score=4,
                distractions=distractions
            )
            db_session.add(reflection)
        db_session.commit()
        
        response = client.get("/reflections/analytics/common-distractions?days=30")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "distractions" in data
        # Phone should be most common
        if data["distractions"]:
            assert data["distractions"][0]["tag"] == "phone"
    
    def test_get_reflections_with_limit(self, client, db_session):
        """Test getting reflections with limit."""
        from models.reflection import Reflection
        
        # Create multiple reflections
        for i in range(5):
            reflection = Reflection(
                date=date.today() - timedelta(days=i+1),
                mood_score=4,
                distractions=[]
            )
            db_session.add(reflection)
        db_session.commit()
        
        response = client.get("/reflections?limit=3")
        assert response.status_code == status.HTTP_200_OK
        
        reflections = response.json()
        assert len(reflections) == 3
