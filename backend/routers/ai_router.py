"""
AI Router
FastAPI endpoints for AI recommendations.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.base import get_db
from models.recommendation_log import RecommendationLog
from models.mood import MoodEntry
from schema.recommendation import (
    RecommendationResponse,
    RecommendationFeedback,
    FeedbackResponse,
    AgentStatsResponse,
    InferFeedbackResponse,
    TaskSuggestion,
    UserPhaseInfo,
)
from ai.config import AIConfig
from ai.hybrid_recommender import HybridRecommender
from ai.reward_calculator import Outcome
from ai.implicit_feedback import ImplicitFeedbackInferencer
from ai.task_selector import TaskSelector
from ai.agent import ScheduleAgent


router = APIRouter(prefix="/ai", tags=["AI"])

# Singleton instances
_recommender = HybridRecommender()
_feedback_inferencer = ImplicitFeedbackInferencer()
_task_selector = TaskSelector()


@router.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(
    user_id: Optional[int] = Query(None, description="User ID (optional in single-user mode)"),
    db: Session = Depends(get_db)
):
    """
    Get an AI-powered task recommendation.
    
    The AI analyzes:
    - Current time of day
    - Your recent mood
    - Pending tasks and priorities
    - Your past preferences (learned over time)
    
    Returns a recommended action with optional task suggestion.
    """
    user_id = AIConfig.get_user_id(user_id)
    
    # Update previous recommendation's next_recommendation_at for implicit feedback
    _update_previous_recommendation(db, user_id)
    
    # Get recommendation
    result = _recommender.get_recommendation(db, user_id)
    
    # Get alternative tasks if applicable
    alternative_tasks = None
    if result.task_id:
        from ai.state import StateSerializer
        from ai.actions import ActionType
        state = StateSerializer.from_key(result.state_key)
        alternatives = _task_selector.get_task_suggestions(
            ActionType(result.action.value), state, db, limit=3
        )
        alternative_tasks = [
            TaskSuggestion(
                id=t.id,
                title=t.title,
                priority=t.priority,
                estimated_duration_minutes=t.estimated_duration,
                deadline=t.deadline
            )
            for t in alternatives if t.id != result.task_id
        ]
    
    # Get current mood for logging
    mood_entry = db.query(MoodEntry).filter(
        MoodEntry.user_id == user_id if not AIConfig.SINGLE_USER_MODE else True
    ).order_by(MoodEntry.timestamp.desc()).first()
    
    # Create log entry
    log = RecommendationLog(
        user_id=user_id,
        state_key=result.state_key,
        state_snapshot={
            "time": datetime.now().isoformat(),
            "state_key": result.state_key,
        },
        action_type=result.action.value,
        suggested_task_id=result.task_id,
        suggested_duration_minutes=result.suggested_duration_minutes,
        confidence=result.confidence,
        strategy_used=result.strategy,
        explanation=result.explanation,
        mood_before=mood_entry.mood if mood_entry else None,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    # Build response
    suggested_task = None
    if result.task_id:
        from models.task import Task
        task = db.query(Task).filter(Task.id == result.task_id).first()
        if task:
            suggested_task = TaskSuggestion(
                id=task.id,
                title=task.title,
                priority=task.priority,
                estimated_duration_minutes=task.estimated_duration,
                deadline=task.deadline
            )
    
    return RecommendationResponse(
        recommendation_id=log.id,
        action_type=result.action.value,
        action_display_name=result.action_display_name,
        suggested_duration_minutes=result.suggested_duration_minutes,
        explanation=result.explanation,
        confidence=result.confidence,
        strategy=result.strategy,
        phase=result.phase,
        suggested_task=suggested_task,
        alternative_tasks=alternative_tasks,
        state_key=result.state_key,
    )


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    feedback: RecommendationFeedback,
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a recommendation.
    
    Feedback helps the AI learn your preferences:
    - Outcome: completed, partial, skipped, ignored
    - Rating: 1-5 stars
    - Mood after: How you feel after the activity
    """
    # Find the recommendation log
    log = db.query(RecommendationLog).filter(
        RecommendationLog.id == feedback.recommendation_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Determine outcome
    outcome = None
    if feedback.outcome:
        try:
            outcome = Outcome(feedback.outcome)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid outcome: {feedback.outcome}. Use: completed, partial, skipped, ignored"
            )
    else:
        # Try to infer outcome
        outcome = _feedback_inferencer.infer_outcome(log, db)
    
    # Update log
    log.outcome = outcome.value
    log.outcome_recorded_at = datetime.now()
    
    if feedback.rating:
        log.user_rating = feedback.rating
    
    if feedback.mood_after:
        log.mood_after = feedback.mood_after
    
    log.was_followed = outcome in (Outcome.COMPLETED, Outcome.PARTIAL)
    
    # Calculate reward and update agent
    from ai.actions import ActionType
    reward = _recommender.record_feedback(
        db=db,
        state_key=log.state_key,
        action=ActionType(log.action_type),
        outcome=outcome,
        user_id=log.user_id,
        mood_before=log.mood_before,
        mood_after=feedback.mood_after,
        user_rating=feedback.rating,
        suggested_duration=log.suggested_duration_minutes,
        actual_duration=feedback.actual_duration_minutes,
    )
    
    log.reward = reward
    db.commit()
    
    # Determine message based on outcome
    if outcome == Outcome.COMPLETED:
        message = "Great job completing the task! 🎉"
    elif outcome == Outcome.PARTIAL:
        message = "Good progress! Every step counts."
    elif outcome == Outcome.SKIPPED:
        message = "No worries, I'll learn from this."
    else:
        message = "Thanks for the feedback!"
    
    return FeedbackResponse(
        success=True,
        reward=reward,
        message=message
    )


@router.get("/stats", response_model=AgentStatsResponse)
def get_stats(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get statistics about the AI recommendation system.
    
    Shows:
    - Learning phase (bootstrap, transition, learned)
    - Number of states explored
    - Exploration rate (epsilon)
    """
    user_id = AIConfig.get_user_id(user_id)
    stats = _recommender.get_stats(user_id)
    
    return AgentStatsResponse(
        user_id=stats["user_id"],
        total_states_visited=stats["total_states_visited"],
        total_visits=stats["total_visits"],
        total_recommendations=stats["total_recommendations"],
        current_epsilon=stats["current_epsilon"],
        phase=stats["phase"],
        phase_thresholds=stats["phase_thresholds"],
    )


@router.get("/phase", response_model=UserPhaseInfo)
def get_phase(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get information about the user's current learning phase.
    """
    user_id = AIConfig.get_user_id(user_id)
    agent = ScheduleAgent.get_instance(user_id)
    
    phase = agent._get_phase()
    total = agent.total_recommendations
    
    # Calculate recommendations until next phase
    until_next = None
    if phase == "bootstrap":
        until_next = AIConfig.BOOTSTRAP_THRESHOLD - total
        description = "Building your profile with rule-based recommendations"
    elif phase == "transition":
        until_next = AIConfig.TRANSITION_THRESHOLD - total
        description = "Learning your patterns with a mix of rules and AI"
    else:
        description = "Personalized recommendations based on your preferences"
    
    return UserPhaseInfo(
        phase=phase,
        total_recommendations=total,
        recommendations_until_next_phase=until_next,
        description=description,
    )


@router.post("/infer-feedback", response_model=InferFeedbackResponse)
def infer_feedback_batch(
    min_age_hours: int = Query(2, ge=1, le=24),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Trigger batch inference of outcomes for old recommendations.
    
    Processes recommendations without explicit feedback that are
    at least min_age_hours old.
    """
    count = _feedback_inferencer.batch_infer_outcomes(db, min_age_hours, limit)
    
    return InferFeedbackResponse(
        processed_count=count,
        message=f"Processed {count} recommendations"
    )


@router.post("/persist")
def persist_agent_models():
    """
    Manually trigger agent model persistence.
    
    This is normally done automatically every 5 minutes.
    """
    saved_count = ScheduleAgent.persist_all()
    return {"saved_count": saved_count, "message": f"Persisted {saved_count} agent models"}


def _update_previous_recommendation(db: Session, user_id: int) -> None:
    """
    Update the previous recommendation's next_recommendation_at timestamp.
    
    This is used for implicit skip detection.
    """
    # Find the most recent recommendation for this user
    prev_log = db.query(RecommendationLog).filter(
        RecommendationLog.user_id == user_id,
        RecommendationLog.next_recommendation_at == None,
        RecommendationLog.outcome == None,
    ).order_by(RecommendationLog.timestamp.desc()).first()
    
    if prev_log:
        prev_log.next_recommendation_at = datetime.now()
        prev_log.activity_gap_seconds = int(
            (datetime.now() - prev_log.timestamp).total_seconds()
        )
        db.commit()
