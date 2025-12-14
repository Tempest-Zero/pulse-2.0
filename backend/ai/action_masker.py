"""
Action Masker
Filters invalid actions based on context to prevent nonsense recommendations.
"""

from typing import List
from sqlalchemy.orm import Session

from .actions import ActionType, ACTION_TYPES, get_all_actions
from .state import UserState
from .config import AIConfig


class ActionMasker:
    """
    Filter and prioritize actions based on context.
    
    Masking rules:
    - Night: Only BREAK allowed
    - Low energy: Block DEEP_FOCUS
    - Low workload: Deprioritize DEEP_FOCUS
    - No high-priority tasks: May block DEEP_FOCUS
    """
    
    def get_valid_actions(
        self,
        state: UserState,
        db: Session = None
    ) -> List[ActionType]:
        """
        Get list of valid actions for the current state.
        
        Args:
            state: Current user state
            db: Optional database session for additional checks
            
        Returns:
            List of allowed ActionType values
        """
        # Start with all actions
        valid = set(get_all_actions())
        
        # Rule 1: Night time - only BREAK
        if state.time_block == "night":
            return [ActionType.BREAK]
        
        # Rule 2: Low energy - no DEEP_FOCUS
        if state.energy_level == "low":
            valid.discard(ActionType.DEEP_FOCUS)
        
        # Rule 3: Time-based restrictions for EXERCISE
        if state.time_block not in ("morning", "evening"):
            valid.discard(ActionType.EXERCISE)
        
        # Rule 4: REFLECT best in morning/evening
        if state.time_block == "afternoon":
            # Don't block, but REFLECT is suboptimal
            pass
        
        # Rule 5: Check database for task availability if provided
        if db:
            valid = self._filter_by_task_availability(valid, state, db)
        
        # Ensure at least one action remains
        if not valid:
            valid = {ActionType.BREAK}  # Safety fallback
        
        return list(valid)
    
    def _filter_by_task_availability(
        self,
        valid_actions: set,
        state: UserState,
        db: Session
    ) -> set:
        """
        Filter actions based on available tasks.
        
        If no high-priority tasks exist, DEEP_FOCUS may be inappropriate.
        """
        from models.task import Task
        
        user_id = AIConfig.get_user_id()
        
        # Check for high-priority tasks (priority >= 4)
        high_priority_count = db.query(Task).filter(
            Task.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            Task.status == "pending",
            Task.priority >= 4,
            Task.is_deleted == False
        ).count()
        
        # If no high-priority tasks and low workload, remove DEEP_FOCUS
        if high_priority_count == 0 and state.workload_pressure == "low":
            valid_actions.discard(ActionType.DEEP_FOCUS)
        
        # Check for any pending tasks
        any_tasks = db.query(Task).filter(
            Task.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            Task.status == "pending",
            Task.is_deleted == False
        ).count()
        
        # If no tasks at all, only allow non-task actions
        if any_tasks == 0:
            valid_actions.discard(ActionType.DEEP_FOCUS)
            valid_actions.discard(ActionType.LIGHT_TASK)
        
        return valid_actions
    
    def get_preferred_actions(
        self,
        state: UserState,
        db: Session = None
    ) -> List[ActionType]:
        """
        Get ordered list of actions from most to least preferred.
        
        Uses both validity and context appropriateness.
        
        Returns:
            Ordered list of actions (most preferred first)
        """
        valid = self.get_valid_actions(state, db)
        
        # Score each valid action
        scored = []
        for action in valid:
            score = self._score_action(action, state)
            scored.append((action, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [action for action, _ in scored]
    
    def _score_action(self, action: ActionType, state: UserState) -> float:
        """
        Score an action's appropriateness for the current context.
        
        Higher score = more appropriate.
        """
        score = 1.0
        meta = ACTION_TYPES[action]
        
        # Time block alignment
        if meta.valid_time_blocks is None:
            score += 0.5  # Always valid
        elif state.time_block in meta.valid_time_blocks:
            score += 1.0
        else:
            score -= 0.5
        
        # Energy alignment
        if meta.min_energy_level:
            energy_order = {"low": 1, "medium": 2, "high": 3}
            required = energy_order.get(meta.min_energy_level, 0)
            current = energy_order.get(state.energy_level, 2)
            if current >= required:
                score += 0.5
            else:
                score -= 1.0
        
        # Workload alignment
        if meta.requires_high_workload:
            if state.workload_pressure == "high":
                score += 0.5
            else:
                score -= 0.5
        
        # Cognitive load vs energy
        if meta.cognitive_load == "high" and state.energy_level == "low":
            score -= 1.5
        elif meta.cognitive_load == "none" and state.energy_level == "high":
            score -= 0.3  # Slight penalty for wasting high energy on nothing
        
        return score
