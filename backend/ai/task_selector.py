"""
Task Selector
Maps action types to concrete tasks from the database.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from .actions import ActionType, ACTION_TYPES
from .state import UserState
from .config import AIConfig


class TaskSelector:
    """
    Select appropriate tasks based on recommended action type.
    
    Maps actions to task criteria:
    - DEEP_FOCUS: high priority, longer duration
    - LIGHT_TASK: low priority, shorter duration
    - Other actions don't map to tasks
    """
    
    # Action type to task filtering criteria
    TASK_CRITERIA = {
        ActionType.DEEP_FOCUS: {
            "min_priority": 3,
            "max_duration_minutes": 120,
            "prefer_deadline": True,
        },
        ActionType.LIGHT_TASK: {
            "max_priority": 3,
            "max_duration_minutes": 45,
            "prefer_deadline": False,
        },
    }
    
    def select_task(
        self,
        action: ActionType,
        state: UserState,
        db: Session
    ) -> Optional["Task"]:
        """
        Select the best task for the given action type.
        
        Args:
            action: The recommended action type
            state: Current user state
            db: Database session
            
        Returns:
            Best matching Task or None if no task fits
        """
        from models.task import Task
        
        # Actions that don't require tasks
        if action not in (ActionType.DEEP_FOCUS, ActionType.LIGHT_TASK):
            return None
        
        criteria = self.TASK_CRITERIA.get(action)
        if not criteria:
            return None
        
        user_id = AIConfig.get_user_id()
        
        # Build base query
        query = db.query(Task).filter(
            Task.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            Task.status == "pending",
            Task.is_deleted == False,
            Task.is_archived == False,
        )
        
        # Apply priority filter
        if "min_priority" in criteria:
            query = query.filter(Task.priority >= criteria["min_priority"])
        if "max_priority" in criteria:
            query = query.filter(Task.priority <= criteria["max_priority"])
        
        # Apply duration filter if task has estimated_duration
        if "max_duration_minutes" in criteria:
            max_dur = criteria["max_duration_minutes"]
            query = query.filter(
                (Task.estimated_duration == None) | 
                (Task.estimated_duration <= max_dur)
            )
        
        # Get candidates
        candidates = query.all()
        
        if not candidates:
            return None
        
        # Score and rank candidates
        scored = [(task, self._score_task(task, action, state)) for task in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored[0][0]
    
    def _score_task(
        self,
        task: "Task",
        action: ActionType,
        state: UserState
    ) -> float:
        """
        Score a task's suitability for the current context.
        
        Factors:
        - Deadline proximity (urgent tasks score higher)
        - Priority alignment
        - Duration match
        """
        score = 0.0
        criteria = self.TASK_CRITERIA.get(action, {})
        
        # Deadline proximity (higher score for closer deadlines)
        if task.deadline:
            now = datetime.now(timezone.utc)
            # Make deadline timezone-aware if it isn't
            deadline = task.deadline if task.deadline.tzinfo else task.deadline.replace(tzinfo=timezone.utc)
            hours_until_deadline = (deadline - now).total_seconds() / 3600
            
            if hours_until_deadline <= 0:
                score += 5.0  # Overdue - highest priority
            elif hours_until_deadline <= 4:
                score += 4.0  # Due within 4 hours
            elif hours_until_deadline <= 24:
                score += 3.0  # Due today
            elif hours_until_deadline <= 72:
                score += 2.0  # Due within 3 days
            else:
                score += 1.0  # Has deadline but not urgent
        
        # Priority score
        score += task.priority  # 1-5 points
        
        # Duration match (prefer tasks that fit suggested duration)
        suggested_duration = ACTION_TYPES[action].suggested_duration_minutes
        if task.estimated_duration:
            duration_ratio = task.estimated_duration / suggested_duration
            if 0.5 <= duration_ratio <= 1.5:
                score += 1.0  # Good fit
            elif duration_ratio > 2.0:
                score -= 0.5  # Task too long for time slot
        
        # Slight preference for older tasks (avoid starvation)
        if task.created_at:
            now = datetime.now(timezone.utc)
            # Make created_at timezone-aware if it isn't
            created_at = task.created_at if task.created_at.tzinfo else task.created_at.replace(tzinfo=timezone.utc)
            days_old = (now - created_at).days
            score += min(days_old * 0.1, 1.0)  # Max 1 point for age
        
        return score
    
    def get_task_suggestions(
        self,
        action: ActionType,
        state: UserState,
        db: Session,
        limit: int = 3
    ) -> List["Task"]:
        """
        Get multiple task suggestions ranked by suitability.
        
        Args:
            action: The recommended action type
            state: Current user state
            db: Database session
            limit: Maximum number of suggestions
            
        Returns:
            List of Task objects, ordered by suitability
        """
        from models.task import Task
        
        if action not in (ActionType.DEEP_FOCUS, ActionType.LIGHT_TASK):
            return []
        
        criteria = self.TASK_CRITERIA.get(action, {})
        user_id = AIConfig.get_user_id()
        
        # Build query
        query = db.query(Task).filter(
            Task.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            Task.status == "pending",
            Task.is_deleted == False,
            Task.is_archived == False,
        )
        
        # Apply filters
        if "min_priority" in criteria:
            query = query.filter(Task.priority >= criteria["min_priority"])
        if "max_priority" in criteria:
            query = query.filter(Task.priority <= criteria["max_priority"])
        
        candidates = query.all()
        
        # Score and sort
        scored = [(task, self._score_task(task, action, state)) for task in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [task for task, _ in scored[:limit]]
