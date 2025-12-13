"""
Reflections CRUD Operations
Handles end-of-day reflection entries with JSON file persistence.
"""

import json
import os
from typing import List, Optional
from datetime import datetime, date

# Data file path
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "reflections.json")


def _ensure_data_file() -> None:
    """Ensure the data directory and file exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"reflections": [], "next_id": 1}, f)


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

def save_reflection(
    mood_score: int,
    distractions: List[str],
    note: str,
    completed_tasks: int,
    total_tasks: int
) -> dict:
    """
    Save an end-of-day reflection.
    
    Args:
        mood_score: 1-5 scale (drained to energized)
        distractions: List of distraction tag IDs
        note: Optional notes about the day
        completed_tasks: Number of tasks completed
        total_tasks: Total number of tasks
    
    Returns:
        The created reflection dict
    """
    data = _read_data()
    
    reflection = {
        "id": data["next_id"],
        "date": date.today().isoformat(),
        "moodScore": mood_score,
        "distractions": distractions,
        "note": note,
        "completedTasks": completed_tasks,
        "totalTasks": total_tasks,
        "createdAt": datetime.now().isoformat()
    }
    
    data["reflections"].append(reflection)
    data["next_id"] += 1
    _write_data(data)
    
    return reflection


def get_reflections(limit: Optional[int] = None) -> List[dict]:
    """
    Get all reflections, most recent first.
    
    Args:
        limit: If provided, return only this many recent reflections
    
    Returns:
        List of reflection dicts
    """
    data = _read_data()
    reflections = sorted(
        data["reflections"],
        key=lambda r: r["date"],
        reverse=True
    )
    
    if limit:
        reflections = reflections[:limit]
    
    return reflections


def get_reflection_by_id(reflection_id: int) -> Optional[dict]:
    """
    Get a single reflection by ID.
    
    Args:
        reflection_id: The reflection ID
    
    Returns:
        Reflection dict or None if not found
    """
    data = _read_data()
    for reflection in data["reflections"]:
        if reflection["id"] == reflection_id:
            return reflection
    return None


def get_reflection_by_date(target_date: str) -> Optional[dict]:
    """
    Get reflection for a specific date.
    
    Args:
        target_date: Date in ISO format (YYYY-MM-DD)
    
    Returns:
        Reflection dict or None if not found
    """
    data = _read_data()
    for reflection in data["reflections"]:
        if reflection["date"] == target_date:
            return reflection
    return None


def update_reflection(reflection_id: int, **updates) -> Optional[dict]:
    """
    Update a reflection's fields.
    
    Args:
        reflection_id: The reflection ID
        **updates: Fields to update
    
    Returns:
        Updated reflection dict or None if not found
    """
    data = _read_data()
    
    for i, reflection in enumerate(data["reflections"]):
        if reflection["id"] == reflection_id:
            allowed = {"moodScore", "distractions", "note"}
            for key, value in updates.items():
                if key in allowed:
                    data["reflections"][i][key] = value
            
            _write_data(data)
            return data["reflections"][i]
    
    return None


def delete_reflection(reflection_id: int) -> bool:
    """
    Delete a reflection.
    
    Args:
        reflection_id: The reflection ID
    
    Returns:
        True if deleted, False if not found
    """
    data = _read_data()
    original_len = len(data["reflections"])
    
    data["reflections"] = [
        r for r in data["reflections"] 
        if r["id"] != reflection_id
    ]
    
    if len(data["reflections"]) < original_len:
        _write_data(data)
        return True
    
    return False


def get_mood_average(days: int = 7) -> Optional[float]:
    """
    Get average mood score over recent days.
    
    Args:
        days: Number of days to average
    
    Returns:
        Average mood score or None if no data
    """
    reflections = get_reflections(limit=days)
    
    if not reflections:
        return None
    
    total = sum(r["moodScore"] for r in reflections)
    return total / len(reflections)


def get_common_distractions(days: int = 30) -> List[tuple]:
    """
    Get most common distractions over recent days.
    
    Args:
        days: Number of days to analyze
    
    Returns:
        List of (distraction_id, count) tuples, sorted by frequency
    """
    reflections = get_reflections(limit=days)
    
    counts = {}
    for reflection in reflections:
        for distraction in reflection.get("distractions", []):
            counts[distraction] = counts.get(distraction, 0) + 1
    
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)
