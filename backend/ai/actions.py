"""
Action Space Definitions
Defines the 5 action types and their metadata for the Q-Learning agent.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ActionType(str, Enum):
    """Action types the AI can recommend."""
    DEEP_FOCUS = "DEEP_FOCUS"
    LIGHT_TASK = "LIGHT_TASK"
    BREAK = "BREAK"
    EXERCISE = "EXERCISE"
    REFLECT = "REFLECT"


@dataclass
class ActionMetadata:
    """Metadata describing an action type."""
    id: str
    display_name: str
    cognitive_load: str  # 'high', 'medium', 'low', 'none'
    suggested_duration_minutes: int
    description: str
    valid_time_blocks: Optional[List[str]] = None  # None means all
    min_energy_level: Optional[str] = None  # 'low', 'medium', 'high'
    requires_high_workload: bool = False


# Action type definitions with full metadata
ACTION_TYPES: dict[ActionType, ActionMetadata] = {
    ActionType.DEEP_FOCUS: ActionMetadata(
        id="DEEP_FOCUS",
        display_name="Deep Focus Work",
        cognitive_load="high",
        suggested_duration_minutes=90,
        description="Tackle complex, high-priority tasks requiring sustained concentration",
        valid_time_blocks=["morning", "afternoon"],
        min_energy_level="medium",
        requires_high_workload=True,
    ),
    ActionType.LIGHT_TASK: ActionMetadata(
        id="LIGHT_TASK",
        display_name="Light Task",
        cognitive_load="low",
        suggested_duration_minutes=30,
        description="Handle simple, routine tasks",
        valid_time_blocks=["morning", "afternoon", "evening"],
        min_energy_level=None,  # Any energy level
    ),
    ActionType.BREAK: ActionMetadata(
        id="BREAK",
        display_name="Take a Break",
        cognitive_load="none",
        suggested_duration_minutes=15,
        description="Rest and recharge",
        valid_time_blocks=None,  # Always valid
        min_energy_level=None,
    ),
    ActionType.EXERCISE: ActionMetadata(
        id="EXERCISE",
        display_name="Exercise",
        cognitive_load="none",
        suggested_duration_minutes=20,
        description="Physical activity to boost energy",
        valid_time_blocks=["morning", "evening"],
        min_energy_level=None,
    ),
    ActionType.REFLECT: ActionMetadata(
        id="REFLECT",
        display_name="Reflect & Plan",
        cognitive_load="medium",
        suggested_duration_minutes=10,
        description="Review progress and plan next steps",
        valid_time_blocks=["morning", "evening"],
        min_energy_level=None,
    ),
}


def get_all_actions() -> List[ActionType]:
    """Return list of all action types."""
    return list(ActionType)


def get_action_metadata(action: ActionType) -> ActionMetadata:
    """Get metadata for a specific action type."""
    return ACTION_TYPES[action]
