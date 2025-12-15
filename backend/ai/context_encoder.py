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
    
    # Time block boundaries (hour of day)
    TIME_BLOCKS = {
        "morning": (6, 12),    # 06:00 - 12:00
        "afternoon": (12, 18), # 12:00 - 18:00
        "evening": (18, 22),   # 18:00 - 22:00
        "night": (22, 6),      # 22:00 - 06:00 (wraps around)
    }
    
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
            user_id: User ID (uses AIConfig.DEFAULT_USER_ID in single-user mode)
            
        Returns:
            UserState with all features encoded
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        user_id = AIConfig.get_user_id(user_id)
        
        # Extract temporal features
        time_block = self._map_hour_to_time_block(current_time.hour)
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
    
    def _map_hour_to_time_block(self, hour: int) -> str:
        """
        Map hour of day to time block.
        
        Args:
            hour: Hour (0-23)
            
        Returns:
            'morning', 'afternoon', 'evening', or 'night'
        """
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
    
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
        - Time of day (morning boost)
        - Tasks completed today (fatigue factor)
        
        Returns:
            'low', 'medium', or 'high'
        """
        from models.mood import MoodEntry
        from models.task import Task
        
        # Get latest mood entry (within last 24 hours)
        latest_mood = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            MoodEntry.timestamp >= current_time.replace(hour=0, minute=0, second=0)
        ).order_by(MoodEntry.timestamp.desc()).first()
        
        # Base mood score
        if latest_mood:
            mood_score = MoodMapper.get_score(latest_mood.mood)
        else:
            mood_score = 5  # Neutral if no mood logged
        
        # Get tasks completed today
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        tasks_completed_today = db.query(Task).filter(
            Task.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            Task.status == "completed",
            Task.completed_at >= today_start,
            Task.is_deleted == False
        ).count()
        
        # Apply circadian rhythm boost
        if time_block == "morning" and tasks_completed_today < 2:
            mood_score += 1
        
        # Apply fatigue penalty
        if tasks_completed_today >= 5:
            mood_score -= 1
        
        # Evening natural decline
        if time_block == "evening":
            mood_score -= 1
        
        # Night severe decline
        if time_block == "night":
            mood_score -= 2
        
        # Clamp to 1-10
        mood_score = max(1, min(10, mood_score))
        
        # Discretize to energy level
        if mood_score >= 8:
            return "high"
        elif mood_score >= 5:
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
        
        # Check for high-priority pending tasks
        high_priority_count = db.query(Task).filter(
            Task.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            Task.status == "pending",
            Task.priority >= 4,
            Task.is_deleted == False
        ).count()
        
        if high_priority_count > 0:
            return "high"
        
        # Check for urgent deadlines (within 24 hours)
        deadline_threshold = current_time + timedelta(hours=24)
        urgent_deadline_count = db.query(Task).filter(
            Task.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True,
            Task.status == "pending",
            Task.deadline != None,
            Task.deadline <= deadline_threshold,
            Task.is_deleted == False
        ).count()
        
        if urgent_deadline_count > 0:
            return "high"
        
        return "low"
