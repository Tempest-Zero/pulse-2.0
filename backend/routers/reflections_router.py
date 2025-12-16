"""
Reflections Router
API endpoints for end-of-day reflection management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from models.base import get_db
from models.reflection import Reflection
from models.user import User
from core.auth import get_current_user
from schema.reflection import ReflectionCreate, ReflectionUpdate, ReflectionResponse

router = APIRouter(prefix="/reflections", tags=["Reflections"])


@router.get("", response_model=List[ReflectionResponse])
def get_reflections(
    limit: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reflections for the current user, most recent first.
    - Use `limit` to get only recent entries
    """
    query = db.query(Reflection).filter(
        Reflection.user_id == current_user.id
    ).order_by(Reflection.date.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


@router.post("", response_model=ReflectionResponse, status_code=status.HTTP_201_CREATED)
def create_reflection(
    reflection_data: ReflectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new reflection for today (for the current user).
    - Only one reflection per day per user allowed
    """
    today = date.today()

    # Check if reflection already exists for today for this user
    existing = db.query(Reflection).filter(
        Reflection.user_id == current_user.id,
        Reflection.date == today
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reflection already exists for today. Use PATCH to update."
        )

    reflection = Reflection(
        user_id=current_user.id,
        date=today,
        mood_score=reflection_data.mood_score,
        distractions=reflection_data.distractions,
        note=reflection_data.note,
        completed_tasks=reflection_data.completed_tasks,
        total_tasks=reflection_data.total_tasks
    )
    db.add(reflection)
    db.commit()
    db.refresh(reflection)
    return reflection


@router.get("/today", response_model=ReflectionResponse)
def get_today_reflection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get today's reflection for the current user if it exists."""
    today = date.today()
    reflection = db.query(Reflection).filter(
        Reflection.user_id == current_user.id,
        Reflection.date == today
    ).first()

    if not reflection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reflection for today yet"
        )

    return reflection


@router.get("/analytics/mood-average")
def get_mood_average(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get average mood score over the current user's recent days."""
    from sqlalchemy import func

    result = db.query(func.avg(Reflection.mood_score)).filter(
        Reflection.user_id == current_user.id
    ).limit(days).scalar()

    return {
        "days": days,
        "average_mood": round(result, 2) if result else None
    }


@router.get("/analytics/common-distractions")
def get_common_distractions(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most common distractions over the current user's recent days."""
    reflections = db.query(Reflection).filter(
        Reflection.user_id == current_user.id
    ).order_by(
        Reflection.date.desc()
    ).limit(days).all()

    counts = {}
    for reflection in reflections:
        for distraction in reflection.distractions or []:
            counts[distraction] = counts.get(distraction, 0) + 1

    sorted_distractions = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "days": days,
        "distractions": [
            {"tag": tag, "count": count}
            for tag, count in sorted_distractions
        ]
    }


@router.get("/{reflection_id}", response_model=ReflectionResponse)
def get_reflection(
    reflection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single reflection by ID (must belong to current user)."""
    reflection = db.query(Reflection).filter(
        Reflection.id == reflection_id,
        Reflection.user_id == current_user.id
    ).first()

    if not reflection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflection not found"
        )

    return reflection


@router.get("/date/{target_date}", response_model=ReflectionResponse)
def get_reflection_by_date(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reflection for a specific date (for the current user)."""
    reflection = db.query(Reflection).filter(
        Reflection.user_id == current_user.id,
        Reflection.date == target_date
    ).first()

    if not reflection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No reflection found for {target_date}"
        )

    return reflection


@router.patch("/{reflection_id}", response_model=ReflectionResponse)
def update_reflection(
    reflection_id: int,
    reflection_data: ReflectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a reflection's fields (must belong to current user)."""
    reflection = db.query(Reflection).filter(
        Reflection.id == reflection_id,
        Reflection.user_id == current_user.id
    ).first()

    if not reflection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflection not found"
        )

    update_data = reflection_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reflection, field, value)

    db.commit()
    db.refresh(reflection)
    return reflection


@router.delete("/{reflection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reflection(
    reflection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a reflection (must belong to current user)."""
    reflection = db.query(Reflection).filter(
        Reflection.id == reflection_id,
        Reflection.user_id == current_user.id
    ).first()

    if not reflection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflection not found"
        )

    db.delete(reflection)
    db.commit()
    return
