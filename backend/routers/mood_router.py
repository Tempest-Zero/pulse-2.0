"""
Mood Router
API endpoints for mood tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from models.base import get_db
from models.mood import MoodEntry, VALID_MOODS
from models.user import User
from core.auth import get_current_user
from schema.mood import MoodCreate, MoodResponse

router = APIRouter(prefix="/mood", tags=["Mood"])


@router.get("/current")
def get_current_mood(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the most recently set mood for the current user."""
    entry = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id
    ).order_by(MoodEntry.timestamp.desc()).first()

    return {
        "mood": entry.mood if entry else "calm",
        "timestamp": entry.timestamp.isoformat() if entry and entry.timestamp else None
    }


@router.post("", response_model=MoodResponse, status_code=status.HTTP_201_CREATED)
def set_mood(
    mood_data: MoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set the current mood for the current user.
    - Valid moods: calm, energized, focused, tired
    - Creates a new entry in mood history
    """
    entry = MoodEntry(
        user_id=current_user.id,
        mood=mood_data.mood
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/history", response_model=List[MoodResponse])
def get_mood_history(
    limit: Optional[int] = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get mood history for the current user, most recent first."""
    query = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id
    ).order_by(MoodEntry.timestamp.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


@router.get("/analytics/counts")
def get_mood_counts(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of each mood in the current user's recent history."""
    entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id
    ).order_by(
        MoodEntry.timestamp.desc()
    ).limit(limit).all()

    counts = {mood: 0 for mood in VALID_MOODS}
    for entry in entries:
        if entry.mood in counts:
            counts[entry.mood] += 1

    return {
        "total_entries": len(entries),
        "counts": counts
    }


@router.get("/analytics/most-common")
def get_most_common_mood(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the most common mood in the current user's recent history."""
    entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id
    ).order_by(
        MoodEntry.timestamp.desc()
    ).limit(limit).all()

    if not entries:
        return {"most_common": None, "count": 0}

    counts = {}
    for entry in entries:
        counts[entry.mood] = counts.get(entry.mood, 0) + 1

    most_common = max(counts, key=counts.get)

    return {
        "most_common": most_common,
        "count": counts[most_common],
        "total_entries": len(entries)
    }


@router.get("/{entry_id}", response_model=MoodResponse)
def get_mood_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single mood entry by ID (must belong to current user)."""
    entry = db.query(MoodEntry).filter(
        MoodEntry.id == entry_id,
        MoodEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )

    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mood_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a mood entry (must belong to current user)."""
    entry = db.query(MoodEntry).filter(
        MoodEntry.id == entry_id,
        MoodEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )

    db.delete(entry)
    db.commit()
    return


@router.delete("/history/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_mood_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear all mood history for the current user."""
    db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id
    ).delete()
    db.commit()
    return
