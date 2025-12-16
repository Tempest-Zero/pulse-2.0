"""
Context Encoder
Converts raw user data and time into UserState for Q-Learning.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from .state import UserState
from .mood_mapper import MoodMapper
from .config import AIConfig


class ContextEncoder:
    """
    Encodes user context into a discrete UserState for Q-Learning.

    Extracts features from:
    - Current time → time_block, day_of_week
    - Recent mood → energy_level
    - Pending tasks → workload_pressure
    """

    # Day names for mapping
    DAY_NAMES = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday"
    ]

    def encode(
        self,
        db: Session,
        current_time: Optional[datetime] = None,
        user_id: Optional[int] = None
    ) -> UserState:
        """
        Encode current context into UserState.

        Args:
            db: Database session
            current_time: Current datetime (defaults to now)
            user_id: User ID (required for multi-user mode)

        Returns:
            UserState with all features encoded
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        user_id = AIConfig.get_user_id(user_id)

        # Extract temporal features using config helper
        time_block = AIConfig.get_time_block(current_time.hour)
        day_of_week = self._map_weekday_to_day_of_week(current_time.weekday())

        # Extract user state features from database
        energy_level = self._calculate_energy_level(db, user_id, time_block, current_time)
        workload_pressure = self._calculate_workload_pressure(db, user_id, current_time)

        return UserState(
            time_block=time_block,
            day_of_week=day_of_week,
            energy_level=energy_level,
            workload_pressure=workload_pressure,
        )

    def _map_weekday_to_day_of_week(self, weekday: int) -> str:
        """
        Map Python weekday (0=Monday) to day name.

        Args:
            weekday: Integer 0-6

        Returns:
            Day name string
        """
        return self.DAY_NAMES[weekday]

    def _calculate_energy_level(
        self,
        db: Session,
        user_id: int,
        time_block: str,
        current_time: datetime
    ) -> str:
        """
        Calculate energy level from mood, time, and activity.

        Uses:
        - Latest mood score
        - Time of day adjustments (configured in AIConfig)
        - Tasks completed today (fatigue factor)

        Returns:
            'low', 'medium', or 'high'
        """
        from models.mood import MoodEntry
        from models.task import Task

        # Get latest mood entry for this user (within last 24 hours)
        latest_mood = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.timestamp >= current_time.replace(hour=0, minute=0, second=0)
        ).order_by(MoodEntry.timestamp.desc()).first()

        # Base mood score
        if latest_mood:
            mood_score = MoodMapper.get_score(latest_mood.mood)
        else:
            mood_score = AIConfig.DEFAULT_MOOD_SCORE

        # Get tasks completed today for this user
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        tasks_completed_today = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "completed",
            Task.completed_at >= today_start,
            Task.is_deleted == False
        ).count()

        # Apply circadian rhythm boost (morning with few tasks = fresh energy)
        if time_block == "morning" and tasks_completed_today < AIConfig.MORNING_BOOST_MAX_TASKS:
            mood_score += AIConfig.MORNING_ENERGY_BOOST

        # Apply fatigue penalty (many tasks completed = cognitive depletion)
        if tasks_completed_today >= AIConfig.FATIGUE_THRESHOLD_TASKS:
            mood_score -= AIConfig.FATIGUE_PENALTY

        # Evening natural decline
        if time_block == "evening":
            mood_score -= AIConfig.EVENING_ENERGY_PENALTY

        # Night severe decline
        if time_block == "night":
            mood_score -= AIConfig.NIGHT_ENERGY_PENALTY

        # Clamp to 1-10
        mood_score = max(1, min(10, mood_score))

        # Discretize to energy level using config thresholds
        if mood_score >= AIConfig.ENERGY_HIGH_THRESHOLD:
            return "high"
        elif mood_score >= AIConfig.ENERGY_MEDIUM_THRESHOLD:
            return "medium"
        else:
            return "low"

    def _calculate_workload_pressure(
        self,
        db: Session,
        user_id: int,
        current_time: datetime
    ) -> str:
        """
        Calculate workload pressure from pending tasks.

        High if:
        - Any high-priority tasks (priority >= 4)
        - Any urgent deadlines (within 24 hours)

        Returns:
            'low' or 'high'
        """
        from models.task import Task
        from datetime import timedelta

        # Check for high-priority pending tasks for this user
        high_priority_count = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "pending",
            Task.priority >= 4,
            Task.is_deleted == False
        ).count()

        if high_priority_count > 0:
            return "high"

        # Check for urgent deadlines (within 24 hours)
        deadline_threshold = current_time + timedelta(hours=24)
        urgent_deadline_count = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "pending",
            Task.deadline != None,
            Task.deadline <= deadline_threshold,
            Task.is_deleted == False
        ).count()

        if urgent_deadline_count > 0:
            return "high"

        return "low"
