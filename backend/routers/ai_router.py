"""
AI Router
FastAPI endpoints for AI-powered recommendations and intelligent scheduling.

This module provides TRUE AI functionality:
- LLM-powered schedule generation (OpenAI/Anthropic with intelligent fallback)
- LLM-powered task breakdown
- Hybrid Q-Learning recommendations
- Context-aware optimization based on user energy, mood, and cognitive load
"""

from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.base import get_db
from models.recommendation_log import RecommendationLog
from models.mood import MoodEntry
from models.user import User
from models.task import Task
from models.schedule import ScheduleBlock
from core.auth import get_current_user
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
from ai.llm_service import get_llm_service
from ai.context_encoder import ContextEncoder
from ai.mood_mapper import MoodMapper


router = APIRouter(prefix="/ai", tags=["AI"])

# Singleton instances
_recommender = HybridRecommender()
_feedback_inferencer = ImplicitFeedbackInferencer()
_task_selector = TaskSelector()
_context_encoder = ContextEncoder()
_mood_mapper = MoodMapper()


@router.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get an AI-powered task recommendation for the current user.

    The AI analyzes:
    - Current time of day
    - Your recent mood
    - Pending tasks and priorities
    - Your past preferences (learned over time)

    Returns a recommended action with optional task suggestion.
    """
    try:
        user_id = current_user.id

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
                ActionType(result.action.value), state, db, user_id=user_id, limit=3
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

        # Get current mood for logging (user's mood only)
        mood_entry = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.timestamp.desc()).first()

        # Create log entry
        log = RecommendationLog(
            user_id=user_id,
            state_key=result.state_key,
            state_snapshot={
                "time": datetime.now(timezone.utc).isoformat(),
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
            task = db.query(Task).filter(
                Task.id == result.task_id,
                Task.user_id == user_id
            ).first()
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
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"[AI] Recommendation error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    feedback: RecommendationFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a recommendation.

    Feedback helps the AI learn your preferences:
    - Outcome: completed, partial, skipped, ignored
    - Rating: 1-5 stars
    - Mood after: How you feel after the activity
    """
    # Find the recommendation log (must belong to current user)
    log = db.query(RecommendationLog).filter(
        RecommendationLog.id == feedback.recommendation_id,
        RecommendationLog.user_id == current_user.id
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
    log.outcome_recorded_at = datetime.now(timezone.utc)

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
        message = "Great job completing the task!"
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about the AI recommendation system for the current user.

    Shows:
    - Learning phase (bootstrap, transition, learned)
    - Number of states explored
    - Exploration rate (epsilon)
    """
    user_id = current_user.id
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the current user's learning phase.
    """
    user_id = current_user.id
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger batch inference of outcomes for the current user's old recommendations.

    Processes recommendations without explicit feedback that are
    at least min_age_hours old.
    """
    count = _feedback_inferencer.batch_infer_outcomes(
        db, min_age_hours, limit, user_id=current_user.id
    )

    return InferFeedbackResponse(
        processed_count=count,
        message=f"Processed {count} recommendations"
    )


@router.post("/persist")
def persist_agent_models(
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger agent model persistence for the current user.

    This is normally done automatically every 5 minutes.
    """
    saved_count = ScheduleAgent.persist_all()
    return {"saved_count": saved_count, "message": f"Persisted {saved_count} agent models"}


@router.post("/breakdown-task/{task_id}")
def breakdown_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Break down a complex task into subtasks using AI analysis.

    This endpoint uses LLM (when available) to intelligently analyze the task
    and create meaningful, actionable subtasks based on:
    - Task type detection (research, writing, development, etc.)
    - Complexity and duration analysis
    - User's current energy level and context
    - Best practices for task decomposition

    Falls back to intelligent rule-based breakdown when no LLM is available.
    """
    # Get the task (must belong to current user)
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id,
        Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if already broken down
    existing_subtasks = db.query(Task).filter(
        Task.parent_id == task_id,
        Task.user_id == current_user.id,
        Task.is_deleted == False
    ).all()
    if existing_subtasks:
        return {
            "message": "Task already broken down",
            "subtasks": [{"id": t.id, "title": t.title, "duration": t.duration} for t in existing_subtasks],
            "ai_powered": False
        }

    # Get user context for personalization
    user_id = current_user.id
    mood_entry = db.query(MoodEntry).filter(
        MoodEntry.user_id == user_id
    ).order_by(MoodEntry.timestamp.desc()).first()

    tasks_completed_today = db.query(Task).filter(
        Task.user_id == user_id,
        Task.completed == True,
        Task.updated_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    ).count()

    user_context = {
        "energy_level": _mood_mapper.mood_to_energy(mood_entry.mood) if mood_entry else "medium",
        "tasks_completed": tasks_completed_today,
        "preferred_session_length": 45  # Default 45-minute sessions
    }

    # Use LLM service for intelligent breakdown
    llm_service = get_llm_service()
    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "duration": task.duration or 2.0,
        "difficulty": task.difficulty or "medium",
        "priority": task.priority or 3,
        "deadline": str(task.deadline) if task.deadline else None
    }

    breakdown = llm_service.breakdown_task_intelligently(task_data, user_context)

    # Create subtasks from breakdown
    created_subtasks = []
    for sub in breakdown.subtasks:
        subtask = Task(
            user_id=current_user.id,
            title=sub.get("title", f"{task.title} - Step"),
            description=sub.get("description", ""),
            duration=sub.get("duration_hours", 0.5),
            difficulty=sub.get("difficulty", task.difficulty),
            parent_id=task_id,
            priority=task.priority,
            estimated_duration=int(sub.get("duration_hours", 0.5) * 60)  # Convert to minutes
        )
        db.add(subtask)
        created_subtasks.append(subtask)

    db.commit()

    # Refresh to get IDs
    for subtask in created_subtasks:
        db.refresh(subtask)

    return {
        "message": f"Task intelligently broken down into {len(created_subtasks)} subtasks",
        "subtasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "duration": t.duration,
                "difficulty": t.difficulty
            }
            for t in created_subtasks
        ],
        "reasoning": breakdown.reasoning,
        "estimated_total_time": breakdown.estimated_total_time,
        "ai_powered": True
    }


@router.post("/generate-schedule")
def generate_ai_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI-optimized schedule using LLM intelligence.

    This endpoint uses TRUE AI to create an optimal schedule:

    **AI Capabilities:**
    - LLM analysis of tasks, priorities, and cognitive requirements
    - Energy-aware scheduling (high-load tasks during peak hours)
    - Ultradian rhythm optimization (90-minute work blocks with breaks)
    - Context-aware placement based on user's current mood and energy
    - Intelligent task batching to minimize context switching
    - Deadline urgency analysis

    **Process:**
    1. Gathers user context (mood, energy, time of day, tasks completed)
    2. Analyzes all pending tasks with their cognitive requirements
    3. Uses LLM (or intelligent fallback) to optimize task placement
    4. Creates schedule blocks with AI-generated reasoning for each placement

    **Fallback:**
    When no LLM API key is available, uses evidence-based productivity
    principles (ultradian rhythms, cognitive load management) for scheduling.

    Returns the generated schedule with AI insights.
    """
    try:
        user_id = current_user.id
        now = datetime.now(timezone.utc)
        current_hour = now.hour

        # Get pending tasks for this user
        pending_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_deleted == False,
            Task.completed == False
        ).order_by(Task.priority.desc(), Task.deadline.asc().nullslast()).all()

        if not pending_tasks:
            return {
                "message": "No pending tasks to schedule",
                "blocks": [],
                "ai_powered": True,
                "optimization_notes": "Add some tasks to get started with AI scheduling!"
            }

        # Get existing fixed blocks for this user
        fixed_blocks = db.query(ScheduleBlock).filter(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.block_type == "fixed"
        ).order_by(ScheduleBlock.start).all()

        # Get user context for AI optimization
        mood_entry = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.timestamp.desc()).first()

        tasks_completed_today = db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == True,
            Task.updated_at >= now.replace(hour=0, minute=0, second=0)
        ).count()

        # Determine energy level from mood
        energy_level = "medium"
        mood_str = "neutral"
        if mood_entry:
            mood_str = mood_entry.mood
            energy_level = _mood_mapper.mood_to_energy(mood_str)

        # Get day of week
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_of_week = days[now.weekday()]

        user_context = {
            "current_hour": current_hour,
            "energy_level": energy_level,
            "mood": mood_str,
            "day_of_week": day_of_week,
            "tasks_completed": tasks_completed_today
        }

        # Format tasks for LLM
        tasks_data = []
        for task in pending_tasks:
            tasks_data.append({
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "priority": task.priority or 3,
                "duration": task.duration or 1.0,
                "difficulty": task.difficulty or "medium",
                "deadline": str(task.deadline) if task.deadline else None
            })

        # Format fixed blocks for LLM
        fixed_data = []
        for block in fixed_blocks:
            fixed_data.append({
                "title": block.title,
                "start": block.start,
                "duration": block.duration,
                "block_type": block.block_type
            })

        # Clear existing task blocks (regenerate schedule)
        db.query(ScheduleBlock).filter(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.block_type.in_(["task", "break"])
        ).delete(synchronize_session=False)

        # Use LLM service for intelligent scheduling
        llm_service = get_llm_service()
        schedule_blocks = llm_service.generate_intelligent_schedule(
            tasks=tasks_data,
            fixed_blocks=fixed_data,
            user_context=user_context,
            working_hours=(9.0, 20.0)
        )

        # Create schedule blocks in database
        created_blocks = []
        scheduled_task_ids = set()

        for ai_block in schedule_blocks:
            block = ScheduleBlock(
                user_id=user_id,
                task_id=ai_block.task_id,
                title=ai_block.title,
                start=ai_block.start_hour,
                duration=ai_block.duration_hours,
                block_type=ai_block.block_type
            )
            db.add(block)
            created_blocks.append({
                "block": block,
                "reasoning": ai_block.reasoning,
                "energy_required": ai_block.energy_required,
                "cognitive_load": ai_block.cognitive_load
            })
            if ai_block.task_id:
                scheduled_task_ids.add(ai_block.task_id)

        db.commit()

        # Refresh blocks to get IDs
        for item in created_blocks:
            db.refresh(item["block"])

        # Build response with AI insights
        response_blocks = []
        for item in created_blocks:
            b = item["block"]
            response_blocks.append({
                "id": b.id,
                "taskId": b.task_id,
                "title": b.title,
                "start": b.start,
                "duration": b.duration,
                "type": b.block_type,
                "reasoning": item["reasoning"],
                "energyRequired": item["energy_required"],
                "cognitiveLoad": item["cognitive_load"]
            })

        # Count unscheduled tasks
        unscheduled_count = len(pending_tasks) - len(scheduled_task_ids)

        # Generate optimization notes
        optimization_notes = _generate_optimization_notes(user_context, len(scheduled_task_ids), unscheduled_count)

        return {
            "message": f"AI-optimized schedule generated with {len(response_blocks)} blocks",
            "blocks": response_blocks,
            "unscheduled_tasks": unscheduled_count,
            "ai_powered": True,
            "user_context": {
                "energy_level": energy_level,
                "mood": mood_str,
                "time_of_day": _get_time_block(current_hour),
                "tasks_completed_today": tasks_completed_today
            },
            "optimization_notes": optimization_notes
        }

    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"[AI] Schedule generation error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


def _get_time_block(hour: int) -> str:
    """Convert hour to human-readable time block."""
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"


def _generate_optimization_notes(user_context: dict, scheduled: int, unscheduled: int) -> str:
    """Generate helpful notes about the schedule optimization."""
    notes = []

    energy = user_context.get("energy_level", "medium")
    time_block = _get_time_block(user_context.get("current_hour", 12))
    tasks_done = user_context.get("tasks_completed", 0)

    if energy == "high" and time_block == "morning":
        notes.append("Peak productivity time! High-priority tasks scheduled for your morning energy surge.")
    elif energy == "low":
        notes.append("Your energy is low - schedule includes strategic breaks to help you recharge.")

    if tasks_done >= 5:
        notes.append(f"Impressive! You've completed {tasks_done} tasks today. Schedule adjusted to prevent burnout.")

    if unscheduled > 0:
        notes.append(f"{unscheduled} task(s) couldn't fit today - consider breaking them down or scheduling tomorrow.")

    if time_block == "evening":
        notes.append("Evening schedule focuses on lighter tasks to wind down naturally.")

    if not notes:
        notes.append("Schedule optimized based on your current energy, priorities, and cognitive load requirements.")

    return " ".join(notes)


@router.get("/smart-recommendation")
def get_smart_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get an LLM-powered smart recommendation for what to do next.

    This endpoint goes beyond the Q-learning system by using LLM to:
    - Understand task descriptions and contexts
    - Analyze recent activity patterns
    - Provide personalized advice with explanations
    - Consider complex factors like burnout prevention

    Returns a recommendation with detailed reasoning and tips.
    """
    try:
        user_id = current_user.id
        now = datetime.now(timezone.utc)
        current_hour = now.hour

        # Get user's current mood
        mood_entry = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.timestamp.desc()).first()

        # Get pending tasks
        pending_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_deleted == False,
            Task.completed == False
        ).order_by(Task.priority.desc(), Task.deadline.asc().nullslast()).all()

        # Get recent activity (last 3 recommendations)
        recent_logs = db.query(RecommendationLog).filter(
            RecommendationLog.user_id == user_id
        ).order_by(RecommendationLog.timestamp.desc()).limit(5).all()

        recent_activity = []
        for log in recent_logs:
            recent_activity.append({
                "action_type": log.action_type,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "outcome": log.outcome,
                "was_followed": log.was_followed
            })

        # Get day of week
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_of_week = days[now.weekday()]

        # Build user state
        energy_level = _mood_mapper.mood_to_energy(mood_entry.mood) if mood_entry else "medium"
        user_state = {
            "time_block": _get_time_block(current_hour),
            "hour": current_hour,
            "energy_level": energy_level,
            "mood": mood_entry.mood if mood_entry else "neutral",
            "day_of_week": day_of_week
        }

        # Format tasks
        tasks_data = []
        for task in pending_tasks[:10]:  # Top 10 tasks
            tasks_data.append({
                "id": task.id,
                "title": task.title,
                "priority": task.priority or 3,
                "duration": task.duration or 1.0,
                "deadline": str(task.deadline) if task.deadline else None
            })

        # Get LLM-powered recommendation
        llm_service = get_llm_service()
        result = llm_service.get_smart_recommendation(
            user_state=user_state,
            available_tasks=tasks_data,
            recent_activity=recent_activity
        )

        # Get the suggested task details if applicable
        suggested_task = None
        if result.get("recommended_task_id"):
            task = db.query(Task).filter(
                Task.id == result["recommended_task_id"],
                Task.user_id == user_id
            ).first()
            if task:
                suggested_task = {
                    "id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                    "duration": task.duration,
                    "deadline": str(task.deadline) if task.deadline else None
                }

        return {
            "action_type": result.get("action_type", "light_task"),
            "reasoning": result.get("reasoning", ""),
            "duration_minutes": result.get("duration_minutes", 45),
            "confidence": result.get("confidence", 0.7),
            "tips": result.get("tips", []),
            "suggested_task": suggested_task,
            "user_context": user_state,
            "ai_powered": True
        }

    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"[AI] Smart recommendation error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


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
        prev_log.next_recommendation_at = datetime.now(timezone.utc)
        prev_log.activity_gap_seconds = int(
            (datetime.now(timezone.utc) - prev_log.timestamp).total_seconds()
        )
        db.commit()
