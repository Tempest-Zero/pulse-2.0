"""
State Representation
168-state space with JSON-safe serialization for Q-Learning.
"""

from dataclasses import dataclass
from typing import Literal, Tuple

# Type definitions for state components
TimeBlock = Literal["morning", "afternoon", "evening", "night"]
DayOfWeek = Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
EnergyLevel = Literal["low", "medium", "high"]
WorkloadPressure = Literal["low", "high"]

# Valid values for validation
VALID_TIME_BLOCKS = ("morning", "afternoon", "evening", "night")
VALID_DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
VALID_ENERGY_LEVELS = ("low", "medium", "high")
VALID_WORKLOAD_PRESSURES = ("low", "high")

# State key separator - pipe character for readability and JSON safety
STATE_KEY_SEPARATOR = "|"


@dataclass(frozen=True)
class UserState:
    """
    Immutable representation of a user's current context.
    
    Total state space: 4 × 7 × 3 × 2 = 168 states
    
    Attributes:
        time_block: Current time of day (morning/afternoon/evening/night)
        day_of_week: Current day (monday through sunday)
        energy_level: User's energy based on mood and activity (low/medium/high)
        workload_pressure: Based on pending high-priority tasks (low/high)
    """
    time_block: TimeBlock
    day_of_week: DayOfWeek
    energy_level: EnergyLevel
    workload_pressure: WorkloadPressure

    def __post_init__(self) -> None:
        """Validate state values on creation."""
        if self.time_block not in VALID_TIME_BLOCKS:
            raise ValueError(f"Invalid time_block: {self.time_block}")
        if self.day_of_week not in VALID_DAYS:
            raise ValueError(f"Invalid day_of_week: {self.day_of_week}")
        if self.energy_level not in VALID_ENERGY_LEVELS:
            raise ValueError(f"Invalid energy_level: {self.energy_level}")
        if self.workload_pressure not in VALID_WORKLOAD_PRESSURES:
            raise ValueError(f"Invalid workload_pressure: {self.workload_pressure}")


class StateSerializer:
    """
    Serialize UserState to/from JSON-compatible string keys.
    
    CRITICAL: Uses pipe-separated strings, NOT tuples, for JSON compatibility.
    Format: "time_block|day_of_week|energy_level|workload_pressure"
    Example: "morning|monday|high|low"
    """

    @staticmethod
    def to_key(state: UserState) -> str:
        """
        Convert UserState to a string key for Q-table storage.
        
        Args:
            state: UserState instance
            
        Returns:
            Pipe-separated string: "morning|monday|high|low"
        """
        return STATE_KEY_SEPARATOR.join([
            state.time_block,
            state.day_of_week,
            state.energy_level,
            state.workload_pressure,
        ])

    @staticmethod
    def from_key(key: str) -> UserState:
        """
        Parse a string key back into a UserState.
        
        Args:
            key: Pipe-separated string key
            
        Returns:
            UserState instance
            
        Raises:
            ValueError: If key format is invalid
        """
        parts = key.split(STATE_KEY_SEPARATOR)
        if len(parts) != 4:
            raise ValueError(
                f"Invalid state key format: expected 4 parts, got {len(parts)}. Key: {key}"
            )
        
        time_block, day_of_week, energy_level, workload_pressure = parts
        
        return UserState(
            time_block=time_block,  # type: ignore
            day_of_week=day_of_week,  # type: ignore
            energy_level=energy_level,  # type: ignore
            workload_pressure=workload_pressure,  # type: ignore
        )

    @staticmethod
    def validate_key(key: str) -> bool:
        """
        Check if a string key is valid.
        
        Args:
            key: String key to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            StateSerializer.from_key(key)
            return True
        except ValueError:
            return False


def generate_all_states() -> list[UserState]:
    """
    Generate all 168 possible states for testing/initialization.
    
    Returns:
        List of all valid UserState combinations
    """
    states = []
    for time_block in VALID_TIME_BLOCKS:
        for day_of_week in VALID_DAYS:
            for energy_level in VALID_ENERGY_LEVELS:
                for workload_pressure in VALID_WORKLOAD_PRESSURES:
                    states.append(UserState(
                        time_block=time_block,  # type: ignore
                        day_of_week=day_of_week,  # type: ignore
                        energy_level=energy_level,  # type: ignore
                        workload_pressure=workload_pressure,  # type: ignore
                    ))
    return states


def get_state_count() -> int:
    """Return the total number of possible states (168)."""
    return (
        len(VALID_TIME_BLOCKS) *
        len(VALID_DAYS) *
        len(VALID_ENERGY_LEVELS) *
        len(VALID_WORKLOAD_PRESSURES)
    )
