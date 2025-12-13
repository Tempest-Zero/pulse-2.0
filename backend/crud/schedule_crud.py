"""
Schedule CRUD Operations
Handles all schedule block operations with JSON file persistence.
"""

import json
import os
from typing import List, Optional
from datetime import datetime

# Data file path
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "schedule.json")


def _ensure_data_file() -> None:
    """Ensure the data directory and file exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"blocks": [], "next_id": 1}, f)


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

def create_block(
    title: str,
    start: float,
    duration: float,
    block_type: str = "fixed"
) -> dict:
    """
    Create a new schedule block.
    
    Args:
        title: Block title
        start: Start hour (e.g., 9.5 for 9:30 AM)
        duration: Duration in hours
        block_type: 'fixed', 'focus', 'break', or 'task'
    
    Returns:
        The created block dict
    """
    data = _read_data()
    
    block = {
        "id": data["next_id"],
        "title": title,
        "start": start,
        "duration": duration,
        "type": block_type,
        "createdAt": datetime.now().isoformat()
    }
    
    data["blocks"].append(block)
    data["next_id"] += 1
    _write_data(data)
    
    return block


def get_blocks(block_type: Optional[str] = None) -> List[dict]:
    """
    Get all schedule blocks, optionally filtered by type.
    
    Args:
        block_type: If provided, filter by block type
    
    Returns:
        List of block dicts
    """
    data = _read_data()
    blocks = data["blocks"]
    
    if block_type is not None:
        blocks = [b for b in blocks if b["type"] == block_type]
    
    return blocks


def get_block_by_id(block_id: int) -> Optional[dict]:
    """
    Get a single block by ID.
    
    Args:
        block_id: The block ID
    
    Returns:
        Block dict or None if not found
    """
    data = _read_data()
    for block in data["blocks"]:
        if block["id"] == block_id:
            return block
    return None


def update_block(block_id: int, **updates) -> Optional[dict]:
    """
    Update a block's fields.
    
    Args:
        block_id: The block ID
        **updates: Fields to update (title, start, duration, type)
    
    Returns:
        Updated block dict or None if not found
    """
    data = _read_data()
    
    for i, block in enumerate(data["blocks"]):
        if block["id"] == block_id:
            allowed = {"title", "start", "duration", "type"}
            for key, value in updates.items():
                if key in allowed:
                    data["blocks"][i][key] = value
            
            _write_data(data)
            return data["blocks"][i]
    
    return None


def delete_block(block_id: int) -> bool:
    """
    Delete a schedule block.
    
    Args:
        block_id: The block ID
    
    Returns:
        True if deleted, False if not found
    """
    data = _read_data()
    original_len = len(data["blocks"])
    
    data["blocks"] = [b for b in data["blocks"] if b["id"] != block_id]
    
    if len(data["blocks"]) < original_len:
        _write_data(data)
        return True
    
    return False


def get_blocks_in_range(start_hour: float, end_hour: float) -> List[dict]:
    """
    Get all blocks that overlap with a time range.
    
    Args:
        start_hour: Start of range
        end_hour: End of range
    
    Returns:
        List of overlapping blocks
    """
    data = _read_data()
    result = []
    
    for block in data["blocks"]:
        block_end = block["start"] + block["duration"]
        # Check for overlap
        if block["start"] < end_hour and block_end > start_hour:
            result.append(block)
    
    return result


def clear_all_blocks() -> int:
    """
    Clear all schedule blocks.
    
    Returns:
        Number of blocks deleted
    """
    data = _read_data()
    count = len(data["blocks"])
    
    data["blocks"] = []
    _write_data(data)
    
    return count
