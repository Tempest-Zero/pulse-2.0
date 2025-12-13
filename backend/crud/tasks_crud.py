"""
Tasks CRUD Operations
Handles all task-related data operations with JSON file persistence.
"""

import json
import os
from typing import List, Optional
from datetime import datetime

# Data file path (relative to crud directory)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")


def _ensure_data_file() -> None:
    """Ensure the data directory and file exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"tasks": [], "next_id": 1}, f)


def _read_data() -> dict:
    """Read data from JSON file."""
    _ensure_data_file()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _write_data(data: dict) -> None:
    """Write data to JSON file."""
    _ensure_data_file()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============ CRUD Operations ============

def create_task(
    title: str,
    duration: float = 1.0,
    difficulty: str = "medium"
) -> dict:
    """
    Create a new task.
    
    Args:
        title: Task title
        duration: Estimated duration in hours
        difficulty: 'easy', 'medium', or 'hard'
    
    Returns:
        The created task dict
    """
    data = _read_data()
    
    task = {
        "id": data["next_id"],
        "title": title,
        "duration": duration,
        "difficulty": difficulty,
        "completed": False,
        "scheduledAt": None,
        "createdAt": datetime.now().isoformat()
    }
    
    data["tasks"].append(task)
    data["next_id"] += 1
    _write_data(data)
    
    return task


def get_tasks(completed: Optional[bool] = None) -> List[dict]:
    """
    Get all tasks, optionally filtered by completion status.
    
    Args:
        completed: If provided, filter by completion status
    
    Returns:
        List of task dicts
    """
    data = _read_data()
    tasks = data["tasks"]
    
    if completed is not None:
        tasks = [t for t in tasks if t["completed"] == completed]
    
    return tasks


def get_task_by_id(task_id: int) -> Optional[dict]:
    """
    Get a single task by ID.
    
    Args:
        task_id: The task ID
    
    Returns:
        Task dict or None if not found
    """
    data = _read_data()
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def update_task(task_id: int, **updates) -> Optional[dict]:
    """
    Update a task's fields.
    
    Args:
        task_id: The task ID
        **updates: Fields to update (title, duration, difficulty, etc.)
    
    Returns:
        Updated task dict or None if not found
    """
    data = _read_data()
    
    for i, task in enumerate(data["tasks"]):
        if task["id"] == task_id:
            # Only update allowed fields
            allowed = {"title", "duration", "difficulty", "completed", "scheduledAt"}
            for key, value in updates.items():
                if key in allowed:
                    data["tasks"][i][key] = value
            
            _write_data(data)
            return data["tasks"][i]
    
    return None


def delete_task(task_id: int) -> bool:
    """
    Delete a task.
    
    Args:
        task_id: The task ID
    
    Returns:
        True if deleted, False if not found
    """
    data = _read_data()
    original_len = len(data["tasks"])
    
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    
    if len(data["tasks"]) < original_len:
        _write_data(data)
        return True
    
    return False


def toggle_task(task_id: int) -> Optional[dict]:
    """
    Toggle a task's completion status.
    
    Args:
        task_id: The task ID
    
    Returns:
        Updated task dict or None if not found
    """
    task = get_task_by_id(task_id)
    if task:
        return update_task(task_id, completed=not task["completed"])
    return None


def schedule_task(task_id: int, start_time: float) -> Optional[dict]:
    """
    Schedule a task at a specific time.
    
    Args:
        task_id: The task ID
        start_time: Start hour (e.g., 9.5 for 9:30 AM)
    
    Returns:
        Updated task dict or None if not found
    """
    return update_task(task_id, scheduledAt=start_time)


def unschedule_task(task_id: int) -> Optional[dict]:
    """
    Remove a task's scheduled time.
    
    Args:
        task_id: The task ID
    
    Returns:
        Updated task dict or None if not found
    """
    return update_task(task_id, scheduledAt=None)
