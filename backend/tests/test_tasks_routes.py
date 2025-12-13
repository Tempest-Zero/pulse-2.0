"""
Tests for tasks API routes.
"""

import pytest
from fastapi import status


class TestTasksRoutes:
    """Test cases for tasks routes."""
    
    def test_get_tasks_empty(self, client):
        """Test getting all tasks when database is empty."""
        response = client.get("/tasks")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_task(self, client):
        """Test creating a new task."""
        task_data = {
            "title": "Complete project",
            "duration": 1.0,
            "difficulty": "hard"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["title"] == "Complete project"
        assert data["duration"] == 1.0
        assert data["difficulty"] == "hard"
        assert data["completed"] == False
        assert "id" in data
    
    def test_get_tasks_with_data(self, client, test_task):
        """Test getting all tasks with data."""
        response = client.get("/tasks")
        assert response.status_code == status.HTTP_200_OK
        
        tasks = response.json()
        assert len(tasks) >= 1
        
        # Find our test task
        task = next((t for t in tasks if t["id"] == test_task.id), None)
        assert task is not None
        assert task["title"] == "Test Task"
    
    def test_get_task_by_id(self, client, test_task):
        """Test getting a single task by ID."""
        response = client.get(f"/tasks/{test_task.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == "Test Task"
    
    def test_get_task_not_found(self, client):
        """Test getting a non-existent task."""
        response = client.get("/tasks/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_task(self, client, test_task):
        """Test updating a task."""
        update_data = {"title": "Updated Task Title"}
        response = client.patch(f"/tasks/{test_task.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["title"] == "Updated Task Title"
        assert data["id"] == test_task.id
    
    def test_delete_task(self, client, test_task):
        """Test deleting a task."""
        response = client.delete(f"/tasks/{test_task.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify task is deleted
        get_response = client.get(f"/tasks/{test_task.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_toggle_task(self, client, test_task):
        """Test toggling a task's completion status."""
        # Initially not completed
        assert test_task.completed == False
        
        # Toggle to completed
        response = client.post(f"/tasks/{test_task.id}/toggle")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["completed"] == True
        
        # Toggle back to not completed
        response = client.post(f"/tasks/{test_task.id}/toggle")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["completed"] == False
    
    def test_schedule_task(self, client, test_task):
        """Test scheduling a task at a specific time."""
        response = client.post(f"/tasks/{test_task.id}/schedule?start_time=14.5")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["scheduledAt"] == 14.5
    
    def test_schedule_task_invalid_time(self, client, test_task):
        """Test scheduling with invalid time."""
        response = client.post(f"/tasks/{test_task.id}/schedule?start_time=25")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_unschedule_task(self, client, test_task, db_session):
        """Test removing a task's scheduled time."""
        # First schedule the task
        test_task.scheduled_at = 10.0
        db_session.commit()
        
        # Unschedule
        response = client.post(f"/tasks/{test_task.id}/unschedule")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["scheduledAt"] is None
    
    def test_filter_tasks_by_completion(self, client, db_session):
        """Test filtering tasks by completion status."""
        from models.task import Task
        
        # Create completed and incomplete tasks
        completed_task = Task(title="Done Task", duration=30, completed=True)
        incomplete_task = Task(title="Todo Task", duration=30, completed=False)
        db_session.add(completed_task)
        db_session.add(incomplete_task)
        db_session.commit()
        
        # Get only completed
        response = client.get("/tasks?completed=true")
        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert all(t["completed"] for t in tasks)
        
        # Get only incomplete
        response = client.get("/tasks?completed=false")
        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert all(not t["completed"] for t in tasks)
