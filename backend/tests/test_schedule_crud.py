"""
Tests for schedule_crud module.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from crud import schedule_crud


@pytest.fixture(autouse=True)
def clean_data():
    """Reset data file before and after each test."""
    data_file = schedule_crud.DATA_FILE
    
    if os.path.exists(data_file):
        os.remove(data_file)
    yield
    if os.path.exists(data_file):
        os.remove(data_file)


class TestCreateBlock:
    """Tests for create_block function."""
    
    def test_create_block_basic(self):
        """Should create a schedule block with default type."""
        block = schedule_crud.create_block("Meeting", 10, 1.5)
        
        assert block["id"] == 1
        assert block["title"] == "Meeting"
        assert block["start"] == 10
        assert block["duration"] == 1.5
        assert block["type"] == "fixed"
    
    def test_create_block_custom_type(self):
        """Should create block with custom type."""
        block = schedule_crud.create_block("Focus Time", 14, 2, "focus")
        
        assert block["type"] == "focus"
    
    def test_create_multiple_blocks_increments_id(self):
        """IDs should auto-increment."""
        b1 = schedule_crud.create_block("Block 1", 9, 1)
        b2 = schedule_crud.create_block("Block 2", 11, 1)
        
        assert b1["id"] == 1
        assert b2["id"] == 2


class TestGetBlocks:
    """Tests for get_blocks function."""
    
    def test_get_blocks_empty(self):
        """Should return empty list when no blocks exist."""
        blocks = schedule_crud.get_blocks()
        assert blocks == []
    
    def test_get_blocks_returns_all(self):
        """Should return all created blocks."""
        schedule_crud.create_block("Block 1", 9, 1)
        schedule_crud.create_block("Block 2", 11, 1)
        
        blocks = schedule_crud.get_blocks()
        assert len(blocks) == 2
    
    def test_get_blocks_filter_by_type(self):
        """Should filter by block type."""
        schedule_crud.create_block("Meeting", 9, 1, "fixed")
        schedule_crud.create_block("Focus", 11, 2, "focus")
        schedule_crud.create_block("Break", 13, 0.5, "break")
        
        fixed = schedule_crud.get_blocks(block_type="fixed")
        focus = schedule_crud.get_blocks(block_type="focus")
        
        assert len(fixed) == 1
        assert len(focus) == 1


class TestGetBlockById:
    """Tests for get_block_by_id function."""
    
    def test_get_existing_block(self):
        """Should return block when ID exists."""
        created = schedule_crud.create_block("Find Me", 10, 1)
        found = schedule_crud.get_block_by_id(created["id"])
        
        assert found is not None
        assert found["title"] == "Find Me"
    
    def test_get_nonexistent_block(self):
        """Should return None for invalid ID."""
        result = schedule_crud.get_block_by_id(999)
        assert result is None


class TestUpdateBlock:
    """Tests for update_block function."""
    
    def test_update_block_title(self):
        """Should update block title."""
        block = schedule_crud.create_block("Original", 10, 1)
        updated = schedule_crud.update_block(block["id"], title="Updated")
        
        assert updated["title"] == "Updated"
    
    def test_update_block_time(self):
        """Should update start time and duration."""
        block = schedule_crud.create_block("Meeting", 10, 1)
        updated = schedule_crud.update_block(block["id"], start=14, duration=2)
        
        assert updated["start"] == 14
        assert updated["duration"] == 2


class TestDeleteBlock:
    """Tests for delete_block function."""
    
    def test_delete_existing_block(self):
        """Should delete block and return True."""
        block = schedule_crud.create_block("Delete Me", 10, 1)
        result = schedule_crud.delete_block(block["id"])
        
        assert result == True
        assert schedule_crud.get_block_by_id(block["id"]) is None
    
    def test_delete_nonexistent_returns_false(self):
        """Should return False for invalid ID."""
        result = schedule_crud.delete_block(999)
        assert result == False


class TestGetBlocksInRange:
    """Tests for get_blocks_in_range function."""
    
    def test_find_overlapping_blocks(self):
        """Should find blocks that overlap with time range."""
        schedule_crud.create_block("Early", 8, 1)   # 8-9
        schedule_crud.create_block("Mid", 10, 2)    # 10-12
        schedule_crud.create_block("Late", 14, 1)   # 14-15
        
        # Range 9-11 should overlap with "Mid" (10-12)
        blocks = schedule_crud.get_blocks_in_range(9, 11)
        
        assert len(blocks) == 1
        assert blocks[0]["title"] == "Mid"
    
    def test_no_overlapping_blocks(self):
        """Should return empty list when no overlap."""
        schedule_crud.create_block("Morning", 8, 1)  # 8-9
        
        blocks = schedule_crud.get_blocks_in_range(12, 14)
        assert blocks == []


class TestClearAllBlocks:
    """Tests for clear_all_blocks function."""
    
    def test_clear_all_blocks(self):
        """Should remove all blocks and return count."""
        schedule_crud.create_block("Block 1", 9, 1)
        schedule_crud.create_block("Block 2", 11, 1)
        schedule_crud.create_block("Block 3", 13, 1)
        
        count = schedule_crud.clear_all_blocks()
        
        assert count == 3
        assert schedule_crud.get_blocks() == []
