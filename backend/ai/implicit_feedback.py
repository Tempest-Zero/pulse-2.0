"""
Implicit Feedback Inferencer
Infers recommendation outcomes from user behavior patterns.
"""

from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Session

from .config import AIConfig
from .reward_calculator import Outcome

if TYPE_CHECKING:
    from models.recommendation_log import RecommendationLog


class ImplicitFeedbackInferencer:
    """
    Infer outcomes from user behavior without explicit feedback.
    
    Inference rules:
    - COMPLETED: Task marked complete within reasonable time
    - PARTIAL: Task started but took too long or incomplete
    - SKIPPED: User requested new recommendation quickly
    - IGNORED: No activity for extended period
    """
    
    def infer_outcome(
        self,
        log: "RecommendationLog",
        db: Session,
        current_time: Optional[datetime] = None
    ) -> Outcome:
        """
        Infer outcome from a recommendation log entry.
        
        Args:
            log: The recommendation log entry
            db: Database session
            current_time: Current time (defaults to now)
            
        Returns:
            Inferred Outcome enum value
        """
        if current_time is None:
            current_time = datetime.now()
        
        # If explicit outcome already set, use it
        if log.outcome:
            try:
                return Outcome(log.outcome)
            except ValueError:
                pass
        
        # Check for task completion
        if log.suggested_task_id:
            outcome = self._check_task_completion(log, db)
            if outcome:
                return outcome
        
        # Check for quick next recommendation (skip detection)
        if log.next_recommendation_at:
            outcome = self._check_skip_detection(log)
            if outcome:
                return outcome
        
        # Check for ignore (long gap with no activity)
        outcome = self._check_ignore_detection(log, current_time)
        if outcome:
            return outcome
        
        # Default to partial if we can't determine
        return Outcome.PARTIAL
    
    def _check_task_completion(
        self, 
        log: "RecommendationLog", 
        db: Session
    ) -> Optional[Outcome]:
        """
        Check if the suggested task was completed.
        
        Returns:
            COMPLETED if task done within 2x suggested time
            PARTIAL if task done but took too long
            None if task not completed
        """
        from models.task import Task
        from ai.actions import ACTION_TYPES, ActionType
        
        if not log.suggested_task_id:
            return None
        
        task = db.query(Task).filter(Task.id == log.suggested_task_id).first()
        if not task:
            return None
        
        # Check if task is completed
        if task.status == "completed" and task.completed_at:
            # Calculate time taken
            time_taken = task.completed_at - log.timestamp
            
            # Get suggested duration for this action type
            try:
                action = ActionType(log.action_type)
                suggested_minutes = ACTION_TYPES[action].suggested_duration_minutes
            except (ValueError, KeyError):
                suggested_minutes = 30  # Default
            
            suggested_duration = timedelta(minutes=suggested_minutes)
            
            # COMPLETED if within 2x suggested duration
            if time_taken <= suggested_duration * 2:
                return Outcome.COMPLETED
            else:
                return Outcome.PARTIAL
        
        # Task in progress counts as partial
        if task.status == "in_progress":
            return Outcome.PARTIAL
        
        return None
    
    def _check_skip_detection(self, log: "RecommendationLog") -> Optional[Outcome]:
        """
        Detect if user skipped by requesting new recommendation quickly.
        
        SKIPPED if next recommendation requested within SKIP_DETECTION_MINUTES.
        """
        if not log.next_recommendation_at:
            return None
        
        time_until_next = log.next_recommendation_at - log.timestamp
        skip_threshold = timedelta(minutes=AIConfig.SKIP_DETECTION_MINUTES)
        
        if time_until_next <= skip_threshold:
            return Outcome.SKIPPED
        
        return None
    
    def _check_ignore_detection(
        self, 
        log: "RecommendationLog",
        current_time: datetime
    ) -> Optional[Outcome]:
        """
        Detect if user ignored the recommendation.
        
        IGNORED if no activity for IGNORE_DETECTION_HOURS and no completion.
        """
        # Use activity_gap_seconds if available
        if log.activity_gap_seconds:
            ignore_threshold_seconds = AIConfig.IGNORE_DETECTION_HOURS * 3600
            if log.activity_gap_seconds >= ignore_threshold_seconds:
                return Outcome.IGNORED
        
        # Fall back to time since recommendation
        time_since_rec = current_time - log.timestamp
        ignore_threshold = timedelta(hours=AIConfig.IGNORE_DETECTION_HOURS)
        
        # Only mark as ignored if enough time has passed AND no completion
        if time_since_rec >= ignore_threshold and not log.was_followed:
            return Outcome.IGNORED
        
        return None
    
    def batch_infer_outcomes(
        self,
        db: Session,
        min_age_hours: int = 2,
        limit: int = 100
    ) -> int:
        """
        Process batch of old recommendations without outcomes.
        
        Args:
            db: Database session
            min_age_hours: Only process logs older than this
            limit: Maximum number to process
            
        Returns:
            Number of logs processed
        """
        from models.recommendation_log import RecommendationLog
        
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=min_age_hours)
        
        # Find logs without outcomes that are old enough
        logs = db.query(RecommendationLog).filter(
            RecommendationLog.outcome == None,
            RecommendationLog.timestamp <= cutoff_time
        ).limit(limit).all()
        
        processed = 0
        for log in logs:
            outcome = self.infer_outcome(log, db, current_time)
            log.outcome = outcome.value
            log.outcome_recorded_at = current_time
            processed += 1
        
        db.commit()
        return processed
