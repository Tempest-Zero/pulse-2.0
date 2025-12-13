"""
Tests for schedule API routes.
"""

import pytest
from fastapi import status


class TestScheduleRoutes:
    """Test cases for schedule routes."""
    
    def test_get_blocks_empty(self, client):
        """Test getting all blocks when database is empty."""
        response = client.get("/schedule")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_block(self, client):
        """Test creating a new schedule block."""
        block_data = {
            "title": "Morning Focus",
            "start": 9.0,
            "duration": 2.0,
            "block_type": "focus"
        }
        response = client.post("/schedule", json=block_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["title"] == "Morning Focus"
        assert data["start"] == 9.0
        assert data["duration"] == 2.0
        assert data["type"] == "focus"
        assert "id" in data
    
    def test_get_blocks_with_data(self, client, test_schedule_block):
        """Test getting all blocks with data."""
        response = client.get("/schedule")
        assert response.status_code == status.HTTP_200_OK
        
        blocks = response.json()
        assert len(blocks) >= 1
        
        block = next((b for b in blocks if b["id"] == test_schedule_block.id), None)
        assert block is not None
        assert block["title"] == "Test Block"
    
    def test_get_block_by_id(self, client, test_schedule_block):
        """Test getting a single block by ID."""
        response = client.get(f"/schedule/{test_schedule_block.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_schedule_block.id
        assert data["title"] == "Test Block"
    
    def test_get_block_not_found(self, client):
        """Test getting a non-existent block."""
        response = client.get("/schedule/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_block(self, client, test_schedule_block):
        """Test updating a schedule block."""
        update_data = {"title": "Updated Block", "duration": 1.5}
        response = client.patch(f"/schedule/{test_schedule_block.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["title"] == "Updated Block"
        assert data["duration"] == 1.5
    
    def test_delete_block(self, client, test_schedule_block):
        """Test deleting a schedule block."""
        response = client.delete(f"/schedule/{test_schedule_block.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify block is deleted
        get_response = client.get(f"/schedule/{test_schedule_block.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_blocks_in_range(self, client, db_session):
        """Test getting blocks that overlap with a time range."""
        from models.schedule import ScheduleBlock
        
        # Create blocks at different times
        blocks_data = [
            {"title": "Early Block", "start": 8.0, "duration": 1.0, "block_type": "focus"},
            {"title": "Mid Block", "start": 10.0, "duration": 2.0, "block_type": "focus"},
            {"title": "Late Block", "start": 14.0, "duration": 1.5, "block_type": "break"},
        ]
        
        for data in blocks_data:
            block = ScheduleBlock(**data)
            db_session.add(block)
        db_session.commit()
        
        # Get blocks in range 9-12 (should get Early Block overlapping and Mid Block)
        response = client.get("/schedule/range?start_hour=9&end_hour=12")
        assert response.status_code == status.HTTP_200_OK
        
        blocks = response.json()
        titles = [b["title"] for b in blocks]
        assert "Mid Block" in titles
    
    def test_filter_by_block_type(self, client, db_session):
        """Test filtering blocks by type."""
        from models.schedule import ScheduleBlock
        
        # Create different block types
        focus_block = ScheduleBlock(title="Focus", start=9.0, duration=1.0, block_type="focus")
        break_block = ScheduleBlock(title="Break", start=10.0, duration=0.5, block_type="break")
        db_session.add(focus_block)
        db_session.add(break_block)
        db_session.commit()
        
        # Get only focus blocks
        response = client.get("/schedule?block_type=focus")
        assert response.status_code == status.HTTP_200_OK
        
        blocks = response.json()
        assert all(b["type"] == "focus" for b in blocks)
    
    def test_clear_all_blocks(self, client, test_schedule_block):
        """Test clearing all schedule blocks."""
        response = client.delete("/schedule")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify all blocks are deleted
        get_response = client.get("/schedule")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json() == []
