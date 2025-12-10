"""
Tests for tasks_crud module.
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from crud import tasks_crud


@pytest.fixture(autouse=True)
def clean_data():
    """Reset data file before and after each test."""
    data_file = tasks_crud.DATA_FILE
    
    # Clean before test
    if os.path.exists(data_file):
        os.remove(data_file)
    
    yield
    
    # Clean after test
    if os.path.exists(data_file):
        os.remove(data_file)


class TestCreateTask:
    """Tests for create_task function."""
    
    def test_create_task_basic(self):
        """Should create a task with default values."""
        task = tasks_crud.create_task("My Task")
        
        assert task["id"] == 1
        assert task["title"] == "My Task"
        assert task["duration"] == 1.0
        assert task["difficulty"] == "medium"
        assert task["completed"] == False
        assert task["scheduledAt"] is None
        assert "createdAt" in task
    
    def test_create_task_custom_values(self):
        """Should create a task with custom duration and difficulty."""
        task = tasks_crud.create_task("Hard Task", duration=2.5, difficulty="hard")
        
        assert task["duration"] == 2.5
        assert task["difficulty"] == "hard"
    
    def test_create_multiple_tasks_increments_id(self):
        """IDs should auto-increment."""
        task1 = tasks_crud.create_task("Task 1")
        task2 = tasks_crud.create_task("Task 2")
        task3 = tasks_crud.create_task("Task 3")
        
        assert task1["id"] == 1
        assert task2["id"] == 2
        assert task3["id"] == 3


class TestGetTasks:
    """Tests for get_tasks function."""
    
    def test_get_tasks_empty(self):
        """Should return empty list when no tasks exist."""
        tasks = tasks_crud.get_tasks()
        assert tasks == []
    
    def test_get_tasks_returns_all(self):
        """Should return all created tasks."""
        tasks_crud.create_task("Task 1")
        tasks_crud.create_task("Task 2")
        
        tasks = tasks_crud.get_tasks()
        assert len(tasks) == 2
    
    def test_get_tasks_filter_completed(self):
        """Should filter by completion status."""
        t1 = tasks_crud.create_task("Task 1")
        tasks_crud.create_task("Task 2")
        tasks_crud.toggle_task(t1["id"])  # Mark first as complete
        
        completed = tasks_crud.get_tasks(completed=True)
        pending = tasks_crud.get_tasks(completed=False)
        
        assert len(completed) == 1
        assert len(pending) == 1


class TestGetTaskById:
    """Tests for get_task_by_id function."""
    
    def test_get_existing_task(self):
        """Should return task when ID exists."""
        created = tasks_crud.create_task("Find Me")
        found = tasks_crud.get_task_by_id(created["id"])
        
        assert found is not None
        assert found["title"] == "Find Me"
    
    def test_get_nonexistent_task(self):
        """Should return None for invalid ID."""
        result = tasks_crud.get_task_by_id(999)
        assert result is None


class TestUpdateTask:
    """Tests for update_task function."""
    
    def test_update_title(self):
        """Should update task title."""
        task = tasks_crud.create_task("Original")
        updated = tasks_crud.update_task(task["id"], title="Updated")
        
        assert updated["title"] == "Updated"
    
    def test_update_multiple_fields(self):
        """Should update multiple fields at once."""
        task = tasks_crud.create_task("Task", duration=1, difficulty="easy")
        updated = tasks_crud.update_task(
            task["id"], 
            duration=3.0, 
            difficulty="hard"
        )
        
        assert updated["duration"] == 3.0
        assert updated["difficulty"] == "hard"
    
    def test_update_nonexistent_returns_none(self):
        """Should return None for invalid ID."""
        result = tasks_crud.update_task(999, title="Nope")
        assert result is None


class TestDeleteTask:
    """Tests for delete_task function."""
    
    def test_delete_existing_task(self):
        """Should delete task and return True."""
        task = tasks_crud.create_task("Delete Me")
        result = tasks_crud.delete_task(task["id"])
        
        assert result == True
        assert tasks_crud.get_task_by_id(task["id"]) is None
    
    def test_delete_nonexistent_returns_false(self):
        """Should return False for invalid ID."""
        result = tasks_crud.delete_task(999)
        assert result == False


class TestToggleTask:
    """Tests for toggle_task function."""
    
    def test_toggle_incomplete_to_complete(self):
        """Should mark incomplete task as complete."""
        task = tasks_crud.create_task("Toggle Me")
        assert task["completed"] == False
        
        toggled = tasks_crud.toggle_task(task["id"])
        assert toggled["completed"] == True
    
    def test_toggle_complete_to_incomplete(self):
        """Should mark complete task as incomplete."""
        task = tasks_crud.create_task("Toggle Me")
        tasks_crud.toggle_task(task["id"])  # Now complete
        
        toggled = tasks_crud.toggle_task(task["id"])
        assert toggled["completed"] == False


class TestScheduleTask:
    """Tests for schedule_task and unschedule_task functions."""
    
    def test_schedule_task(self):
        """Should set scheduledAt time."""
        task = tasks_crud.create_task("Schedule Me")
        scheduled = tasks_crud.schedule_task(task["id"], 9.5)
        
        assert scheduled["scheduledAt"] == 9.5
    
    def test_unschedule_task(self):
        """Should clear scheduledAt time."""
        task = tasks_crud.create_task("Unschedule Me")
        tasks_crud.schedule_task(task["id"], 10.0)
        
        unscheduled = tasks_crud.unschedule_task(task["id"])
        assert unscheduled["scheduledAt"] is None
