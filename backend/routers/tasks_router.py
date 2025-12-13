"""
Tasks Router
API endpoints for task management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from models.base import get_db
from models.task import Task
from schema.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
def get_tasks(
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all tasks.
    - Filter by completion status with `completed` query param
    - Supports pagination with skip/limit
    """
    query = db.query(Task)
    
    if completed is not None:
        query = query.filter(Task.completed == completed)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task."""
    # Get duration in hours (handles conversion from minutes if provided)
    duration_hours = task_data.get_duration_hours()
    
    task = Task(
        title=task_data.title,
        duration=duration_hours,
        difficulty=task_data.difficulty,
        priority=task_data.priority
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get a single task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task's fields."""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    return


@router.post("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Toggle a task's completion status."""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.completed = not task.completed
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/schedule", response_model=TaskResponse)
def schedule_task(
    task_id: int,
    start_time: float,
    db: Session = Depends(get_db)
):
    """Schedule a task at a specific time."""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if start_time < 0 or start_time > 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be between 0 and 24"
        )
    
    task.scheduled_at = start_time
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/unschedule", response_model=TaskResponse)
def unschedule_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Remove a task's scheduled time."""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.scheduled_at = None
    db.commit()
    db.refresh(task)
    return task
