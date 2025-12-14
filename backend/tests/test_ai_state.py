"""
AI State Serialization Tests
Tests for state representation and JSON-safe serialization.
"""

import pytest
import json
from ai.state import (
    UserState, 
    StateSerializer, 
    generate_all_states, 
    get_state_count,
    VALID_TIME_BLOCKS,
    VALID_DAYS,
    VALID_ENERGY_LEVELS,
    VALID_WORKLOAD_PRESSURES,
)


class TestUserState:
    """Tests for UserState dataclass."""
    
    def test_create_valid_state(self):
        """Test creating a valid UserState."""
        state = UserState(
            time_block="morning",
            day_of_week="monday",
            energy_level="high",
            workload_pressure="low"
        )
        assert state.time_block == "morning"
        assert state.day_of_week == "monday"
        assert state.energy_level == "high"
        assert state.workload_pressure == "low"
    
    def test_state_is_immutable(self):
        """Test that UserState is frozen (immutable)."""
        state = UserState("morning", "monday", "high", "low")
        with pytest.raises(AttributeError):
            state.time_block = "afternoon"
    
    def test_invalid_time_block(self):
        """Test validation of invalid time_block."""
        with pytest.raises(ValueError) as exc:
            UserState("invalid", "monday", "high", "low")
        assert "Invalid time_block" in str(exc.value)
    
    def test_invalid_day_of_week(self):
        """Test validation of invalid day_of_week."""
        with pytest.raises(ValueError) as exc:
            UserState("morning", "invalid", "high", "low")
        assert "Invalid day_of_week" in str(exc.value)
    
    def test_invalid_energy_level(self):
        """Test validation of invalid energy_level."""
        with pytest.raises(ValueError) as exc:
            UserState("morning", "monday", "invalid", "low")
        assert "Invalid energy_level" in str(exc.value)
    
    def test_invalid_workload_pressure(self):
        """Test validation of invalid workload_pressure."""
        with pytest.raises(ValueError) as exc:
            UserState("morning", "monday", "high", "invalid")
        assert "Invalid workload_pressure" in str(exc.value)


class TestStateSerializer:
    """Tests for StateSerializer."""
    
    def test_to_key_format(self):
        """Test state → key conversion format."""
        state = UserState("morning", "monday", "high", "low")
        key = StateSerializer.to_key(state)
        assert key == "morning|monday|high|low"
    
    def test_to_key_pipe_separator(self):
        """Test that key uses pipe separator."""
        state = UserState("afternoon", "friday", "medium", "high")
        key = StateSerializer.to_key(state)
        assert "|" in key
        assert key.count("|") == 3
    
    def test_from_key_parsing(self):
        """Test key → state parsing."""
        key = "evening|saturday|low|high"
        state = StateSerializer.from_key(key)
        assert state.time_block == "evening"
        assert state.day_of_week == "saturday"
        assert state.energy_level == "low"
        assert state.workload_pressure == "high"
    
    def test_roundtrip_conversion(self):
        """Test state → key → state roundtrip."""
        original = UserState("night", "sunday", "medium", "low")
        key = StateSerializer.to_key(original)
        restored = StateSerializer.from_key(key)
        assert original == restored
    
    def test_json_serialization(self):
        """Test that key is JSON-serializable (CRITICAL)."""
        state = UserState("morning", "monday", "high", "low")
        key = StateSerializer.to_key(state)
        
        # Must be serializable as JSON
        data = {"state": key, "value": 1.5}
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        
        assert parsed["state"] == key
        assert isinstance(parsed["state"], str)
    
    def test_from_key_invalid_format(self):
        """Test parsing invalid key raises ValueError."""
        with pytest.raises(ValueError) as exc:
            StateSerializer.from_key("invalid|key")
        assert "expected 4 parts" in str(exc.value)
    
    def test_from_key_too_many_parts(self):
        """Test parsing key with too many parts."""
        with pytest.raises(ValueError):
            StateSerializer.from_key("a|b|c|d|e")
    
    def test_validate_key_valid(self):
        """Test validate_key returns True for valid keys."""
        assert StateSerializer.validate_key("morning|monday|high|low") is True
    
    def test_validate_key_invalid(self):
        """Test validate_key returns False for invalid keys."""
        assert StateSerializer.validate_key("invalid") is False


class TestGenerateAllStates:
    """Tests for state generation."""
    
    def test_generate_all_168_states(self):
        """Test generating all 168 states."""
        states = generate_all_states()
        assert len(states) == 168
    
    def test_get_state_count(self):
        """Test state count calculation."""
        assert get_state_count() == 168
    
    def test_all_states_unique(self):
        """Test all generated states are unique."""
        states = generate_all_states()
        keys = [StateSerializer.to_key(s) for s in states]
        assert len(keys) == len(set(keys))
    
    def test_all_states_serializable(self):
        """Test all 168 states can be serialized to JSON."""
        states = generate_all_states()
        q_table = {}
        
        for state in states:
            key = StateSerializer.to_key(state)
            q_table[key] = {"DEEP_FOCUS": 0.5, "BREAK": 0.5}
        
        # Must be JSON-serializable
        json_str = json.dumps(q_table)
        parsed = json.loads(json_str)
        
        assert len(parsed) == 168
        assert all(isinstance(k, str) for k in parsed.keys())


class TestStateConstants:
    """Tests for state constant values."""
    
    def test_valid_time_blocks(self):
        """Test time block constants."""
        assert set(VALID_TIME_BLOCKS) == {"morning", "afternoon", "evening", "night"}
    
    def test_valid_days(self):
        """Test day of week constants."""
        assert len(VALID_DAYS) == 7
        assert "monday" in VALID_DAYS
        assert "sunday" in VALID_DAYS
    
    def test_valid_energy_levels(self):
        """Test energy level constants."""
        assert set(VALID_ENERGY_LEVELS) == {"low", "medium", "high"}
    
    def test_valid_workload_pressures(self):
        """Test workload pressure constants."""
        assert set(VALID_WORKLOAD_PRESSURES) == {"low", "high"}
