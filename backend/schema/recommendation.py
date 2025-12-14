"""
Recommendation Schemas
Pydantic models for AI recommendation API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# --- Request Schemas ---

class RecommendationFeedback(BaseModel):
    """Feedback for a recommendation."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recommendation_id": 42,
            "outcome": "completed",
            "rating": 5,
            "mood_after": "energized",
            "actual_duration_minutes": 45
        }
    })

    recommendation_id: int = Field(..., description="ID of the recommendation log")
    outcome: Optional[str] = Field(None, description="completed, partial, skipped, ignored")
    rating: Optional[int] = Field(None, ge=1, le=5, description="User rating 1-5")
    mood_after: Optional[str] = Field(None, description="Current mood after activity")
    actual_duration_minutes: Optional[int] = Field(None, ge=0, description="Actual time spent")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


# --- Response Schemas ---

class TaskSuggestion(BaseModel):
    """A suggested task from the AI."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    priority: int
    estimated_duration_minutes: Optional[int] = None
    deadline: Optional[datetime] = None


class RecommendationResponse(BaseModel):
    """Response from the AI recommendation endpoint."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recommendation_id": 42,
            "action_type": "DEEP_FOCUS",
            "action_display_name": "Deep Focus Work",
            "suggested_duration_minutes": 90,
            "explanation": "Personalized for you: Tackle complex, high-priority tasks",
            "confidence": 0.85,
            "strategy": "rl",
            "phase": "learned",
            "suggested_task": {
                "id": 15,
                "title": "Complete project proposal",
                "priority": 4,
                "estimated_duration_minutes": 60,
                "deadline": "2025-12-15T17:00:00"
            },
            "state_key": "morning|monday|high|high"
        }
    })

    recommendation_id: int = Field(..., description="Log ID for feedback")
    action_type: str = Field(..., description="DEEP_FOCUS, LIGHT_TASK, BREAK, etc.")
    action_display_name: str = Field(..., description="Human-readable action name")
    suggested_duration_minutes: int = Field(..., description="Suggested activity duration")
    explanation: str = Field(..., description="Why this was recommended")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence 0-1")
    strategy: str = Field(..., description="rule, rl, or hybrid")
    phase: str = Field(..., description="bootstrap, transition, or learned")
    
    # Task details (if applicable)
    suggested_task: Optional[TaskSuggestion] = None
    alternative_tasks: Optional[List[TaskSuggestion]] = None
    
    # State info (for debugging)
    state_key: str = Field(..., description="Encoded state for feedback")


class FeedbackResponse(BaseModel):
    """Response after submitting feedback."""
    success: bool
    reward: float = Field(..., description="Calculated reward value")
    message: str


class AgentStatsResponse(BaseModel):
    """Statistics about the AI agent."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": 1,
            "total_states_visited": 24,
            "total_visits": 85,
            "total_recommendations": 72,
            "current_epsilon": 0.12,
            "phase": "learned",
            "phase_thresholds": {
                "bootstrap": 20,
                "transition": 60
            }
        }
    })

    user_id: int
    total_states_visited: int
    total_visits: int
    total_recommendations: int
    current_epsilon: float
    phase: str
    phase_thresholds: dict


class UserPhaseInfo(BaseModel):
    """Information about the user's learning phase."""
    phase: str = Field(..., description="bootstrap, transition, or learned")
    total_recommendations: int
    recommendations_until_next_phase: Optional[int] = None
    description: str


class InferFeedbackResponse(BaseModel):
    """Response from batch inference endpoint."""
    processed_count: int
    message: str
