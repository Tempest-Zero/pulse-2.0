"""
Smart Schedule Router - Integrated 3-Layer Architecture

API endpoints following the architecture:
- /api/extract → Layer 1: LangGraph + LLM (Brain)
- /api/schedule → Layer 2: OR-Tools CP-SAT (Solver)
- /api/feedback → Layer 3: Graphiti + Neo4j (Memory)

Data Flow:
- Context → Extraction (Layer 3 feeds Layer 1)
- Patterns → Solver (Layer 3 feeds Layer 2)
- Feedback → Storage (User feedback to Layer 3)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime, date
import asyncio

from models.base import get_db
from models.user import User
from core.auth import get_current_user

# Layer 1: Brain (LangGraph + LLM)
from langgraph_flow import extraction_graph, ExtractionState
from langgraph_flow.schemas import TaskSchema, ExtractionResultSchema

# Layer 2: Solver (OR-Tools CP-SAT)
from scheduler import (
    generate_schedule,
    ScheduleRequest,
    ScheduleResponse,
    TaskInput as SolverTaskInput,
    FixedSlot,
    UserPreferences,
)

# Layer 3: Memory (Graphiti + Neo4j)
from graphiti_client.resilient_client import resilient_client, patterns_to_constraints
from graphiti_client.pattern_extractor import store_edit, store_user_defaults

router = APIRouter(prefix="/api", tags=["Smart Schedule"])


# ==================== Request/Response Schemas ====================

class ExtractRequest(BaseModel):
    """Request for NLP extraction (Layer 1)."""
    message: str = Field(..., min_length=1, max_length=5000,
                         description="Natural language input from user")
    conversation_id: Optional[str] = Field(None, description="For multi-turn dialog")


class ExtractResponse(BaseModel):
    """Response from extraction layer."""
    success: bool
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    extracted_data: Optional[dict] = None
    message: str


class ScheduleGenerateRequest(BaseModel):
    """Request to generate schedule (Layer 2)."""
    tasks: List[dict] = Field(..., description="Tasks from extraction or manual input")
    fixed_slots: List[dict] = Field(default=[], description="Fixed time commitments")
    day_start_time: str = Field(default="09:00", description="Day start in HH:MM")
    day_end_time: str = Field(default="22:00", description="Day end in HH:MM")
    schedule_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD")
    preferences: Optional[dict] = None


class ScheduleBlock(BaseModel):
    """A scheduled time block."""
    task_name: str
    start_time: str
    end_time: str
    reason: str


class ScheduleGenerateResponse(BaseModel):
    """Response with generated schedule."""
    success: bool
    status: Literal["optimal", "feasible", "infeasible", "partial"]
    schedule: List[ScheduleBlock]
    overflow_tasks: List[str] = []
    message: str
    error: Optional[str] = None


class FeedbackRequest(BaseModel):
    """User feedback for schedule edit (Layer 3)."""
    feedback_type: Literal["accepted", "edited", "rejected"]
    task_name: str
    original_time: Optional[str] = None  # "HH:MM" for edits
    new_time: Optional[str] = None  # "HH:MM" for edits
    reason: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response from feedback storage."""
    success: bool
    message: str
    pattern_learned: bool = False


class UserDefaultsRequest(BaseModel):
    """User defaults for cold start."""
    wake_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    sleep_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")


# ==================== Layer 1: Extract (Brain) ====================

@router.post("/extract", response_model=ExtractResponse)
async def extract_tasks(
    request: ExtractRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Layer 1: NLP Extraction using LangGraph + LLM

    Extracts structured task data from natural language input.
    Supports multi-turn dialog for clarification.
    Uses user context from Layer 3 (Graphiti) for personalization.
    """
    try:
        # Get user context from Layer 3 (Memory)
        user_context = await resilient_client.get_user_context(str(current_user.id))

        # Build initial state for LangGraph
        from langchain_core.messages import HumanMessage

        initial_state: ExtractionState = {
            "user_id": str(current_user.id),
            "messages": [HumanMessage(content=request.message)],
            "user_context": user_context,
            "extracted_data": None,
            "validation_issues": [],
            "attempt_count": 0,
            "final_result": None,
        }

        # Run extraction graph
        result = await extraction_graph.ainvoke(initial_state)

        # Check if clarification needed
        if result.get("validation_issues") and not result.get("final_result"):
            # Get the last AI message (clarification question)
            ai_messages = [m for m in result.get("messages", [])
                         if hasattr(m, 'type') and m.type == 'ai']
            clarification = ai_messages[-1].content if ai_messages else "Could you provide more details?"

            return ExtractResponse(
                success=True,
                needs_clarification=True,
                clarification_question=clarification,
                extracted_data=result.get("extracted_data"),
                message="Need more information to complete extraction"
            )

        # Return final extracted data
        final_data = result.get("final_result") or result.get("extracted_data") or {}

        return ExtractResponse(
            success=True,
            needs_clarification=False,
            extracted_data=final_data,
            message=f"Successfully extracted {len(final_data.get('tasks', []))} tasks"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )


# ==================== Layer 2: Schedule (Solver) ====================

@router.post("/schedule", response_model=ScheduleGenerateResponse)
async def generate_smart_schedule(
    request: ScheduleGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Layer 2: Schedule Generation using OR-Tools CP-SAT

    Generates optimized schedule using constraint satisfaction.
    Incorporates learned patterns from Layer 3 (Graphiti).
    """
    try:
        # Get learned constraints from Layer 3 (Memory)
        user_context = await resilient_client.get_user_context(str(current_user.id))
        patterns = user_context.get("patterns", {})
        learned_constraints = patterns_to_constraints(patterns)

        # Convert tasks to solver format
        solver_tasks = []
        schedule_date = date.fromisoformat(request.schedule_date) if request.schedule_date else date.today()

        for task in request.tasks:
            solver_tasks.append(SolverTaskInput(
                name=task.get("name", "Unnamed Task"),
                priority=task.get("priority", "medium"),
                estimated_time_hours=task.get("estimated_time_hours", 1.0),
                deadline=schedule_date,
                difficulty=task.get("difficulty", "medium"),
                is_optional=task.get("is_optional", False),
            ))

        # Convert fixed slots
        fixed_slots = [
            FixedSlot(
                name=slot.get("name", "Fixed"),
                start_time=slot.get("start_time"),
                end_time=slot.get("end_time"),
            )
            for slot in request.fixed_slots
        ]

        # Build preferences
        prefs_data = request.preferences or {}
        preferences = UserPreferences(
            energy_peak=prefs_data.get("energy_peak", "morning"),
            mood=prefs_data.get("mood", "normal"),
            work_style=prefs_data.get("work_style", "balanced"),
        )

        # Create schedule request
        schedule_request = ScheduleRequest(
            tasks=solver_tasks,
            fixed_slots=fixed_slots,
            preferences=preferences,
            day_start_time=request.day_start_time,
            day_end_time=request.day_end_time,
            date=schedule_date,
        )

        # Generate schedule with learned constraints
        result: ScheduleResponse = generate_schedule(schedule_request, learned_constraints)

        # Convert to response format
        schedule_blocks = [
            ScheduleBlock(
                task_name=block.task_name,
                start_time=block.start_time,
                end_time=block.end_time,
                reason=block.reason,
            )
            for block in result.schedule
        ]

        return ScheduleGenerateResponse(
            success=result.status in ["optimal", "feasible"],
            status=result.status,
            schedule=schedule_blocks,
            overflow_tasks=result.overflow_tasks,
            message=f"Generated schedule with {len(schedule_blocks)} blocks",
            error=result.error,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schedule generation failed: {str(e)}"
        )


# ==================== Layer 3: Feedback (Memory) ====================

@router.post("/feedback", response_model=FeedbackResponse)
async def store_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Layer 3: Feedback Storage using Graphiti + Neo4j

    Stores user feedback for pattern learning.
    Edits are stored as temporal facts for future schedule optimization.
    """
    try:
        user_id = str(current_user.id)
        pattern_learned = False

        if request.feedback_type == "edited":
            # Store edit for pattern learning
            edit_data = {
                "task_name": request.task_name,
                "from_time": request.original_time,
                "to_time": request.new_time,
                "action": "move",
                "reason": request.reason,
            }

            success = await resilient_client.store_edit(user_id, edit_data)
            pattern_learned = success

            message = "Edit recorded for pattern learning" if success else "Edit queued (will sync when available)"

        elif request.feedback_type == "accepted":
            # Store acceptance (positive reinforcement)
            from graphiti_client.store import store_acceptance
            await store_acceptance(user_id, {
                "task_name": request.task_name,
                "accepted_time": request.original_time or request.new_time,
            })
            message = "Acceptance recorded"

        else:  # rejected
            message = "Rejection noted"

        return FeedbackResponse(
            success=True,
            message=message,
            pattern_learned=pattern_learned,
        )

    except Exception as e:
        # Non-fatal - queue for later
        return FeedbackResponse(
            success=False,
            message=f"Feedback queued: {str(e)}",
            pattern_learned=False,
        )


@router.post("/user-defaults", response_model=FeedbackResponse)
async def set_user_defaults(
    request: UserDefaultsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Store user defaults (wake/sleep time) for cold start.
    """
    try:
        user_id = str(current_user.id)
        success = await resilient_client.store_user_defaults(
            user_id,
            request.wake_time,
            request.sleep_time
        )

        return FeedbackResponse(
            success=success,
            message="User defaults saved" if success else "Defaults queued for sync",
            pattern_learned=False,
        )

    except Exception as e:
        return FeedbackResponse(
            success=False,
            message=f"Error saving defaults: {str(e)}",
            pattern_learned=False,
        )


# ==================== Combined Endpoint ====================

class FullScheduleRequest(BaseModel):
    """Combined request for full flow."""
    description: str = Field(..., description="Natural language task description")
    day_start_time: str = Field(default="09:00")
    day_end_time: str = Field(default="22:00")
    schedule_date: Optional[str] = None
    fixed_slots: List[dict] = []


class FullScheduleResponse(BaseModel):
    """Combined response with extraction + schedule."""
    success: bool
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    extracted_tasks: List[dict] = []
    schedule: List[ScheduleBlock] = []
    overflow_tasks: List[str] = []
    message: str


@router.post("/generate", response_model=FullScheduleResponse)
async def generate_full_schedule(
    request: FullScheduleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Full pipeline: Extract → Schedule

    Combines Layer 1 (extraction) and Layer 2 (scheduling) in one call.
    Uses Layer 3 (memory) for context and patterns.
    """
    try:
        # Step 1: Extract tasks (Layer 1)
        extract_response = await extract_tasks(
            ExtractRequest(message=request.description),
            current_user
        )

        if extract_response.needs_clarification:
            return FullScheduleResponse(
                success=True,
                needs_clarification=True,
                clarification_question=extract_response.clarification_question,
                extracted_tasks=extract_response.extracted_data.get("tasks", []) if extract_response.extracted_data else [],
                message="Need clarification before scheduling"
            )

        extracted_data = extract_response.extracted_data or {}
        tasks = extracted_data.get("tasks", [])

        if not tasks:
            return FullScheduleResponse(
                success=False,
                message="No tasks could be extracted from your description"
            )

        # Step 2: Generate schedule (Layer 2)
        schedule_response = await generate_smart_schedule(
            ScheduleGenerateRequest(
                tasks=tasks,
                fixed_slots=request.fixed_slots + extracted_data.get("fixed_slots", []),
                day_start_time=extracted_data.get("wake_time") or request.day_start_time,
                day_end_time=extracted_data.get("sleep_time") or request.day_end_time,
                schedule_date=request.schedule_date,
                preferences=extracted_data.get("preferences"),
            ),
            current_user
        )

        return FullScheduleResponse(
            success=schedule_response.success,
            extracted_tasks=tasks,
            schedule=schedule_response.schedule,
            overflow_tasks=schedule_response.overflow_tasks,
            message=f"Extracted {len(tasks)} tasks, scheduled {len(schedule_response.schedule)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(e)}"
        )


# ==================== Health/Status ====================

@router.get("/status")
async def get_layer_status():
    """Check status of all three layers."""

    # Check Layer 3 (Graphiti/Neo4j)
    neo4j_available = resilient_client.is_available()
    queue_size = resilient_client.get_queue_size("_health_check")

    return {
        "layer1_brain": {
            "status": "ready",
            "engine": "LangGraph + OpenAI"
        },
        "layer2_solver": {
            "status": "ready",
            "engine": "OR-Tools CP-SAT"
        },
        "layer3_memory": {
            "status": "connected" if neo4j_available else "fallback",
            "engine": "Graphiti + Neo4j",
            "queued_operations": queue_size,
        }
    }
