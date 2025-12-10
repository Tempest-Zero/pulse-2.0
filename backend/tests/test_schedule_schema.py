"""
Tests for schedule schemas.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pydantic import ValidationError
from schema.schedule import ScheduleBlockCreate, ScheduleBlockUpdate, ScheduleBlockResponse


class TestScheduleBlockCreate:
    """Tests for ScheduleBlockCreate schema."""
    
    def test_valid_block_required_fields(self):
        """Should create block with required fields."""
        block = ScheduleBlockCreate(title="Meeting", start=9, duration=1)
        
        assert block.title == "Meeting"
        assert block.start == 9
        assert block.duration == 1
        assert block.block_type == "fixed"
    
    def test_valid_block_all_fields(self):
        """Should create block with all fields."""
        block = ScheduleBlockCreate(
            title="Focus Time",
            start=14.5,
            duration=2,
            block_type="focus"
        )
        
        assert block.block_type == "focus"
    
    def test_invalid_empty_title(self):
        """Should reject empty title."""
        with pytest.raises(ValidationError):
            ScheduleBlockCreate(title="", start=9, duration=1)
    
    def test_invalid_start_negative(self):
        """Should reject negative start hour."""
        with pytest.raises(ValidationError):
            ScheduleBlockCreate(title="Block", start=-1, duration=1)
    
    def test_invalid_start_over_24(self):
        """Should reject start hour over 24."""
        with pytest.raises(ValidationError):
            ScheduleBlockCreate(title="Block", start=25, duration=1)
    
    def test_invalid_duration_too_short(self):
        """Should reject duration less than 0.25h."""
        with pytest.raises(ValidationError):
            ScheduleBlockCreate(title="Block", start=9, duration=0.1)
    
    def test_invalid_block_type(self):
        """Should reject invalid block type."""
        with pytest.raises(ValidationError):
            ScheduleBlockCreate(title="Block", start=9, duration=1, block_type="invalid")
    
    def test_valid_block_types(self):
        """Should accept all valid block types."""
        for btype in ["fixed", "focus", "break", "task"]:
            block = ScheduleBlockCreate(title="Block", start=9, duration=1, block_type=btype)
            assert block.block_type == btype


class TestScheduleBlockUpdate:
    """Tests for ScheduleBlockUpdate schema."""
    
    def test_all_fields_optional(self):
        """Should allow empty update."""
        update = ScheduleBlockUpdate()
        
        assert update.title is None
        assert update.start is None
        assert update.duration is None
    
    def test_partial_update(self):
        """Should allow partial updates."""
        update = ScheduleBlockUpdate(start=10.5, duration=2)
        
        assert update.start == 10.5
        assert update.duration == 2
        assert update.title is None


class TestScheduleBlockResponse:
    """Tests for ScheduleBlockResponse schema."""
    
    def test_response_from_dict(self):
        """Should create response from dict."""
        data = {
            "id": 1,
            "title": "Meeting",
            "start": 9,
            "duration": 1.5,
            "type": "fixed",  # Uses alias
            "created_at": None,
        }
        response = ScheduleBlockResponse(**data)
        
        assert response.id == 1
        assert response.block_type == "fixed"
