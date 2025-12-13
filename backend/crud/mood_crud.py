"""
Mood CRUD Operations
Handles mood tracking with JSON file persistence.
"""

import json
import os
from typing import List, Optional
from datetime import datetime

# Data file path
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "mood.json")

# Valid mood states (matching frontend)
VALID_MOODS = {"calm", "energized", "focused", "tired"}


def _ensure_data_file() -> None:
    """Ensure the data directory and file exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "current": "calm",
                "history": [],
                "next_id": 1
            }, f)


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

def set_mood(mood: str) -> dict:
    """
    Set the current mood and log to history.
    
    Args:
        mood: One of 'calm', 'energized', 'focused', 'tired'
    
    Returns:
        The mood entry dict
    
    Raises:
        ValueError: If mood is not valid
    """
    if mood not in VALID_MOODS:
        raise ValueError(f"Invalid mood: {mood}. Must be one of {VALID_MOODS}")
    
    data = _read_data()
    
    entry = {
        "id": data["next_id"],
        "mood": mood,
        "timestamp": datetime.now().isoformat()
    }
    
    data["current"] = mood
    data["history"].append(entry)
    data["next_id"] += 1
    _write_data(data)
    
    return entry


def get_current_mood() -> str:
    """
    Get the current mood.
    
    Returns:
        Current mood string
    """
    data = _read_data()
    return data["current"]


def get_mood_history(limit: Optional[int] = None) -> List[dict]:
    """
    Get mood history, most recent first.
    
    Args:
        limit: If provided, return only this many recent entries
    
    Returns:
        List of mood entry dicts
    """
    data = _read_data()
    history = sorted(
        data["history"],
        key=lambda h: h["timestamp"],
        reverse=True
    )
    
    if limit:
        history = history[:limit]
    
    return history


def get_mood_by_id(entry_id: int) -> Optional[dict]:
    """
    Get a single mood entry by ID.
    
    Args:
        entry_id: The entry ID
    
    Returns:
        Mood entry dict or None if not found
    """
    data = _read_data()
    for entry in data["history"]:
        if entry["id"] == entry_id:
            return entry
    return None


def delete_mood_entry(entry_id: int) -> bool:
    """
    Delete a mood history entry.
    
    Args:
        entry_id: The entry ID
    
    Returns:
        True if deleted, False if not found
    """
    data = _read_data()
    original_len = len(data["history"])
    
    data["history"] = [h for h in data["history"] if h["id"] != entry_id]
    
    if len(data["history"]) < original_len:
        _write_data(data)
        return True
    
    return False


def get_mood_counts(limit: int = 100) -> dict:
    """
    Get count of each mood in recent history.
    
    Args:
        limit: Number of recent entries to analyze
    
    Returns:
        Dict mapping mood to count
    """
    history = get_mood_history(limit=limit)
    
    counts = {mood: 0 for mood in VALID_MOODS}
    for entry in history:
        mood = entry["mood"]
        if mood in counts:
            counts[mood] += 1
    
    return counts


def get_most_common_mood(limit: int = 100) -> Optional[str]:
    """
    Get the most common mood in recent history.
    
    Args:
        limit: Number of recent entries to analyze
    
    Returns:
        Most common mood string or None if no history
    """
    counts = get_mood_counts(limit=limit)
    
    if not any(counts.values()):
        return None
    
    return max(counts, key=counts.get)


def clear_history() -> int:
    """
    Clear all mood history (keeps current mood).
    
    Returns:
        Number of entries deleted
    """
    data = _read_data()
    count = len(data["history"])
    
    data["history"] = []
    data["next_id"] = 1
    _write_data(data)
    
    return count
