"""
Rule Engine
Heuristic-based fallback for cold-start and low-confidence situations.
"""

from typing import Tuple
from .actions import ActionType
from .state import UserState


class RuleEngine:
    """
    Rule-based recommendation engine.
    
    Used during bootstrap phase and as fallback when RL confidence is low.
    Provides sensible defaults based on time, energy, and workload.
    """
    
    def get_recommendation(self, state: UserState) -> Tuple[ActionType, str]:
        """
        Get a rule-based recommendation with explanation.
        
        Rule priority:
        1. Night → BREAK (always)
        2. High workload + high/medium energy → DEEP_FOCUS
        3. Morning high energy → DEEP_FOCUS or LIGHT_TASK
        4. Low energy → BREAK
        5. Evening → REFLECT
        6. Default → LIGHT_TASK
        
        Args:
            state: Current user state
            
        Returns:
            Tuple of (action, explanation)
        """
        # Rule 1: Night time - always suggest break
        if state.time_block == "night":
            return (
                ActionType.BREAK,
                "It's late - time to rest and recharge for tomorrow."
            )
        
        # Rule 2: High workload + sufficient energy → Deep focus
        if state.workload_pressure == "high" and state.energy_level in ("high", "medium"):
            if state.time_block in ("morning", "afternoon"):
                return (
                    ActionType.DEEP_FOCUS,
                    "You have high-priority work and good energy - perfect time for deep focus."
                )
        
        # Rule 3: Morning with high energy
        if state.time_block == "morning" and state.energy_level == "high":
            if state.workload_pressure == "high":
                return (
                    ActionType.DEEP_FOCUS,
                    "Morning is ideal for tackling complex tasks while your mind is fresh."
                )
            else:
                return (
                    ActionType.LIGHT_TASK,
                    "Start your day with some easy wins to build momentum."
                )
        
        # Rule 4: Low energy → Break
        if state.energy_level == "low":
            return (
                ActionType.BREAK,
                "Your energy is low - a short break will help you recharge."
            )
        
        # Rule 5: Evening → Reflect
        if state.time_block == "evening":
            return (
                ActionType.REFLECT,
                "Evening is a good time to review your day and plan ahead."
            )
        
        # Rule 6: Weekend with high energy and low workload → Exercise
        if state.day_of_week in ("saturday", "sunday"):
            if state.energy_level == "high" and state.workload_pressure == "low":
                return (
                    ActionType.EXERCISE,
                    "Weekend with good energy - a great time for physical activity!"
                )
        
        # Rule 7: Afternoon with medium energy → Light task
        if state.time_block == "afternoon" and state.energy_level == "medium":
            return (
                ActionType.LIGHT_TASK,
                "Afternoon slump? Tackle some lighter tasks to stay productive."
            )
        
        # Default: Light task
        return (
            ActionType.LIGHT_TASK,
            "Let's work on something manageable to make progress."
        )
    
    def get_all_rules(self) -> list[dict]:
        """
        Return documentation of all rules for transparency.
        
        Returns:
            List of rule descriptions
        """
        return [
            {
                "priority": 1,
                "condition": "time_block == 'night'",
                "action": "BREAK",
                "rationale": "Rest during night hours"
            },
            {
                "priority": 2,
                "condition": "workload_pressure == 'high' AND energy_level in ('high', 'medium') AND time_block in ('morning', 'afternoon')",
                "action": "DEEP_FOCUS",
                "rationale": "Tackle priority work when energy allows"
            },
            {
                "priority": 3,
                "condition": "time_block == 'morning' AND energy_level == 'high'",
                "action": "DEEP_FOCUS or LIGHT_TASK",
                "rationale": "Capitalize on morning freshness"
            },
            {
                "priority": 4,
                "condition": "energy_level == 'low'",
                "action": "BREAK",
                "rationale": "Recharge when depleted"
            },
            {
                "priority": 5,
                "condition": "time_block == 'evening'",
                "action": "REFLECT",
                "rationale": "Review and plan during wind-down"
            },
            {
                "priority": 6,
                "condition": "weekend AND high energy AND low workload",
                "action": "EXERCISE",
                "rationale": "Physical activity when free time available"
            },
            {
                "priority": 7,
                "condition": "time_block == 'afternoon' AND energy_level == 'medium'",
                "action": "LIGHT_TASK",
                "rationale": "Maintain productivity during afternoon slump"
            },
            {
                "priority": 8,
                "condition": "default",
                "action": "LIGHT_TASK",
                "rationale": "Safe default for progress"
            },
        ]
