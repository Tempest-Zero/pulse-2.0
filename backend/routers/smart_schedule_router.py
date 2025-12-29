"""
Smart Schedule Router
API endpoints for natural language task input and schedule generation.
Designed to integrate with OR-Tools constraint solver.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from models.base import get_db
from models.user import User
from core.auth import get_current_user

router = APIRouter(prefix="/smart-schedule", tags=["Smart Schedule"])


# ============== Request/Response Schemas ==============

class TaskInput(BaseModel):
    """Individual task parsed from description or provided by solver."""
    name: str = Field(..., min_length=1, max_length=255)
    duration: int = Field(..., ge=5, le=480, description="Duration in minutes")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    deadline: Optional[datetime] = None


class SmartScheduleRequest(BaseModel):
    """Request to generate schedule from natural language description."""
    description: str = Field(..., min_length=10, max_length=5000, 
                             description="Natural language description of tasks")
    start_hour: float = Field(default=9.0, ge=0, le=24, 
                              description="Start of scheduling window (24h format)")
    end_hour: float = Field(default=20.0, ge=0, le=24, 
                            description="End of scheduling window (24h format)")
    break_duration: int = Field(default=15, ge=0, le=60, 
                                description="Break duration between tasks in minutes")


class ScheduledTask(BaseModel):
    """A task with assigned time slot."""
    id: int
    name: str
    start_time: str  # "HH:MM" format
    end_time: str    # "HH:MM" format
    duration: int    # Duration in minutes
    priority: Optional[str] = None
    tip: Optional[str] = None


class SmartScheduleResponse(BaseModel):
    """Response with generated schedule."""
    success: bool
    message: str
    tasks_found: int
    scheduled_tasks: List[ScheduledTask]
    total_duration: int  # Total minutes
    scheduling_window: dict  # {start: "HH:MM", end: "HH:MM"}


class ParsedTasksResponse(BaseModel):
    """Response with just parsed tasks (no scheduling)."""
    success: bool
    message: str
    tasks: List[TaskInput]


# ============== OR-Tools Integration Points ==============

def parse_tasks_from_description(description: str) -> List[dict]:
    """
    Parse natural language description into individual tasks.
    
    TODO: This is a placeholder for OR-Tools integration.
    Replace this function with your NLP/parsing logic.
    
    Args:
        description: Natural language text describing tasks
        
    Returns:
        List of task dictionaries with name, estimated duration, priority
    """
    # Simple sentence-based parsing as placeholder
    # Your OR-Tools integration can replace this
    sentences = description.replace('\n', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
    
    tasks = []
    for i, sentence in enumerate(sentences):
        # Simple heuristic for duration estimation based on word count
        word_count = len(sentence.split())
        
        if word_count > 15:
            duration = 60
        elif word_count > 10:
            duration = 45
        elif word_count > 5:
            duration = 30
        else:
            duration = 15
            
        # Simple priority detection based on keywords
        priority = "medium"
        lower_sentence = sentence.lower()
        if any(word in lower_sentence for word in ["urgent", "important", "asap", "critical", "deadline"]):
            priority = "high"
        elif any(word in lower_sentence for word in ["optional", "if time", "maybe", "later"]):
            priority = "low"
        
        tasks.append({
            "name": sentence[:100],  # Cap name length
            "duration": duration,
            "priority": priority
        })
    
    return tasks


def generate_schedule_with_solver(
    tasks: List[dict],
    start_hour: float,
    end_hour: float,
    break_duration: int,
    fixed_blocks: List[dict] = None
) -> List[dict]:
    """
    Generate optimized schedule using constraint solver.
    
    TODO: This is the integration point for your OR-Tools solver.
    Replace this function with your CP-SAT based scheduling logic.
    
    Args:
        tasks: List of tasks with name, duration, priority
        start_hour: Start of available window (0-24)
        end_hour: End of available window (0-24)
        break_duration: Minutes of break between tasks
        fixed_blocks: Existing schedule blocks to avoid (from class schedule, etc.)
        
    Returns:
        List of scheduled tasks with time assignments
    """
    # Placeholder: Simple sequential scheduling
    # Your OR-Tools solver should replace this with optimized scheduling
    
    scheduled = []
    current_hour = start_hour
    current_minutes = int((start_hour % 1) * 60)
    
    for i, task in enumerate(tasks):
        task_duration_hours = task["duration"] / 60
        
        # Check if task fits before end hour
        if current_hour + task_duration_hours > end_hour:
            break
            
        # Format start time
        start_time = f"{int(current_hour):02d}:{current_minutes:02d}"
        
        # Calculate end time
        total_minutes = current_minutes + task["duration"]
        end_hour_calc = int(current_hour) + total_minutes // 60
        end_minutes = total_minutes % 60
        end_time = f"{end_hour_calc:02d}:{end_minutes:02d}"
        
        scheduled.append({
            "id": i + 1,
            "name": task["name"],
            "start_time": start_time,
            "end_time": end_time,
            "duration": task["duration"],
            "priority": task.get("priority", "medium"),
            "tip": get_productivity_tip()
        })
        
        # Move to next slot with break
        current_minutes = end_minutes + break_duration
        current_hour = end_hour_calc + current_minutes // 60
        current_minutes = current_minutes % 60
    
    return scheduled


def get_productivity_tip() -> str:
    """Get a random productivity tip."""
    import random
    tips = [
        "Use the Pomodoro technique for better focus",
        "Take a 5-min walk before starting this",
        "Put your phone in another room",
        "Play lofi beats to stay in the zone",
        "Grab a snack before diving in",
        "Set a timer so you don't lose track",
        "Start with the hardest part first",
        "Keep water nearby to stay hydrated",
        "Clear your desk before beginning",
        "Take deep breaths to center yourself",
    ]
    return random.choice(tips)


# ============== API Endpoints ==============

@router.post("/parse", response_model=ParsedTasksResponse)
def parse_description(
    request: SmartScheduleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Parse natural language description into tasks without scheduling.
    Useful for previewing what tasks were detected.
    """
    try:
        parsed_tasks = parse_tasks_from_description(request.description)
        
        if not parsed_tasks:
            return ParsedTasksResponse(
                success=False,
                message="No tasks could be identified from the description. Try being more specific.",
                tasks=[]
            )
        
        tasks = [
            TaskInput(
                name=t["name"],
                duration=t["duration"],
                priority=t.get("priority")
            ) 
            for t in parsed_tasks
        ]
        
        return ParsedTasksResponse(
            success=True,
            message=f"Successfully parsed {len(tasks)} tasks from your description",
            tasks=tasks
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing description: {str(e)}"
        )


@router.post("/generate", response_model=SmartScheduleResponse)
def generate_smart_schedule(
    request: SmartScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an optimized schedule from natural language description.
    
    This endpoint:
    1. Parses the description into individual tasks
    2. Retrieves existing schedule blocks to avoid conflicts
    3. Uses the solver to generate optimal time assignments
    4. Returns the complete schedule
    
    Integration Point: The `generate_schedule_with_solver` function
    should be replaced with your OR-Tools CP-SAT implementation.
    """
    try:
        # Step 1: Parse tasks from description
        parsed_tasks = parse_tasks_from_description(request.description)
        
        if not parsed_tasks:
            return SmartScheduleResponse(
                success=False,
                message="No tasks found in description. Please describe your tasks more clearly.",
                tasks_found=0,
                scheduled_tasks=[],
                total_duration=0,
                scheduling_window={
                    "start": f"{int(request.start_hour):02d}:{int((request.start_hour % 1) * 60):02d}",
                    "end": f"{int(request.end_hour):02d}:{int((request.end_hour % 1) * 60):02d}"
                }
            )
        
        # Step 2: Get existing fixed blocks (optional, for conflict avoidance)
        # You can fetch from database here if needed:
        # from models.schedule import ScheduleBlock
        # fixed_blocks = db.query(ScheduleBlock).filter(
        #     ScheduleBlock.user_id == current_user.id,
        #     ScheduleBlock.block_type == "fixed"
        # ).all()
        
        # Step 3: Generate schedule using solver
        scheduled_tasks = generate_schedule_with_solver(
            tasks=parsed_tasks,
            start_hour=request.start_hour,
            end_hour=request.end_hour,
            break_duration=request.break_duration,
            fixed_blocks=None  # Pass fixed_blocks here when integrating
        )
        
        if not scheduled_tasks:
            return SmartScheduleResponse(
                success=False,
                message="Could not fit any tasks in the available time window",
                tasks_found=len(parsed_tasks),
                scheduled_tasks=[],
                total_duration=0,
                scheduling_window={
                    "start": f"{int(request.start_hour):02d}:{int((request.start_hour % 1) * 60):02d}",
                    "end": f"{int(request.end_hour):02d}:{int((request.end_hour % 1) * 60):02d}"
                }
            )
        
        # Convert to response format
        response_tasks = [
            ScheduledTask(**task) for task in scheduled_tasks
        ]
        
        total_duration = sum(t.duration for t in response_tasks)
        
        return SmartScheduleResponse(
            success=True,
            message=f"Successfully scheduled {len(response_tasks)} out of {len(parsed_tasks)} tasks",
            tasks_found=len(parsed_tasks),
            scheduled_tasks=response_tasks,
            total_duration=total_duration,
            scheduling_window={
                "start": f"{int(request.start_hour):02d}:{int((request.start_hour % 1) * 60):02d}",
                "end": f"{int(request.end_hour):02d}:{int((request.end_hour % 1) * 60):02d}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating schedule: {str(e)}"
        )


@router.post("/generate-from-tasks", response_model=SmartScheduleResponse)
def generate_from_tasks(
    tasks: List[TaskInput],
    start_hour: float = 9.0,
    end_hour: float = 20.0,
    break_duration: int = 15,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate schedule from pre-parsed task list.
    
    Use this endpoint when you want to:
    - Bypass natural language parsing
    - Provide tasks directly from another source
    - Test the scheduler with specific task configurations
    """
    try:
        task_dicts = [t.model_dump() for t in tasks]
        
        scheduled_tasks = generate_schedule_with_solver(
            tasks=task_dicts,
            start_hour=start_hour,
            end_hour=end_hour,
            break_duration=break_duration
        )
        
        response_tasks = [ScheduledTask(**task) for task in scheduled_tasks]
        total_duration = sum(t.duration for t in response_tasks)
        
        return SmartScheduleResponse(
            success=True,
            message=f"Scheduled {len(response_tasks)} tasks",
            tasks_found=len(tasks),
            scheduled_tasks=response_tasks,
            total_duration=total_duration,
            scheduling_window={
                "start": f"{int(start_hour):02d}:{int((start_hour % 1) * 60):02d}",
                "end": f"{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating schedule: {str(e)}"
        )
