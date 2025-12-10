"""
Tests for task schemas.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pydantic import ValidationError
from schema.task import TaskCreate, TaskUpdate, TaskResponse


class TestTaskCreate:
    """Tests for TaskCreate schema."""
    
    def test_valid_task_minimal(self):
        """Should create task with just title."""
        task = TaskCreate(title="My Task")
        
        assert task.title == "My Task"
        assert task.duration == 1.0
        assert task.difficulty == "medium"
    
    def test_valid_task_all_fields(self):
        """Should create task with all fields."""
        task = TaskCreate(title="Hard Task", duration=2.5, difficulty="hard")
        
        assert task.title == "Hard Task"
        assert task.duration == 2.5
        assert task.difficulty == "hard"
    
    def test_invalid_empty_title(self):
        """Should reject empty title."""
        with pytest.raises(ValidationError):
            TaskCreate(title="")
    
    def test_invalid_duration_too_short(self):
        """Should reject duration less than 0.25h."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", duration=0.1)
    
    def test_invalid_duration_too_long(self):
        """Should reject duration more than 8h."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", duration=10.0)
    
    def test_invalid_difficulty(self):
        """Should reject invalid difficulty."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", difficulty="super_hard")
    
    def test_valid_difficulties(self):
        """Should accept all valid difficulties."""
        for diff in ["easy", "medium", "hard"]:
            task = TaskCreate(title="Task", difficulty=diff)
            assert task.difficulty == diff


class TestTaskUpdate:
    """Tests for TaskUpdate schema."""
    
    def test_all_fields_optional(self):
        """Should allow empty update."""
        update = TaskUpdate()
        
        assert update.title is None
        assert update.duration is None
        assert update.difficulty is None
        assert update.completed is None
    
    def test_partial_update(self):
        """Should allow partial updates."""
        update = TaskUpdate(title="New Title", completed=True)
        
        assert update.title == "New Title"
        assert update.completed == True
        assert update.duration is None
    
    def test_scheduled_at_validation(self):
        """Should validate scheduled_at range."""
        update = TaskUpdate(scheduled_at=9.5)
        assert update.scheduled_at == 9.5
        
        with pytest.raises(ValidationError):
            TaskUpdate(scheduled_at=25.0)  # Invalid hour


class TestTaskResponse:
    """Tests for TaskResponse schema."""
    
    def test_response_from_dict(self):
        """Should create response from dict."""
        data = {
            "id": 1,
            "title": "Test Task",
            "duration": 1.5,
            "difficulty": "medium",
            "completed": False,
            "scheduled_at": None,
            "created_at": None,
            "updated_at": None,
        }
        response = TaskResponse(**data)
        
        assert response.id == 1
        assert response.title == "Test Task"
    
    def test_response_alias_fields(self):
        """Should handle camelCase aliases."""
        data = {
            "id": 1,
            "title": "Test",
            "duration": 1.0,
            "difficulty": "easy",
            "completed": True,
            "scheduledAt": 10.5,  # camelCase
            "createdAt": None,
        }
        response = TaskResponse(**data)
        
        assert response.scheduled_at == 10.5
