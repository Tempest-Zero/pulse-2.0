"""
Feedback Router
Endpoints for submitting and retrieving user feedback.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional, List

from models.base import get_db
from models.user import User
from models.feedback import Feedback
from core.auth import get_current_user


router = APIRouter(prefix="/feedback", tags=["Feedback"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class FeedbackCreate(BaseModel):
    """Request body for creating feedback."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    category: str = Field(default="general", description="Feedback category")
    review: Optional[str] = Field(None, max_length=2000, description="Optional review text")


class FeedbackResponse(BaseModel):
    """Response for a single feedback entry."""
    id: int
    userId: int
    username: Optional[str] = None
    rating: int
    category: str
    review: Optional[str] = None
    createdAt: Optional[str] = None


class FeedbackStats(BaseModel):
    """Statistics about feedback."""
    totalFeedback: int
    averageRating: float
    ratingDistribution: dict


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/stats", response_model=FeedbackStats)
def get_feedback_stats(
    db: Session = Depends(get_db)
):
    """
    Get overall feedback statistics (public endpoint).
    """
    try:
        # Get total count
        total = db.query(func.count(Feedback.id)).scalar() or 0
        
        # Get average rating (handle None when no feedback exists)
        avg_result = db.query(func.avg(Feedback.rating)).scalar()
        avg_rating = float(avg_result) if avg_result is not None else 0.0
        
        # Get rating distribution
        distribution = {}
        for i in range(1, 6):
            count = db.query(func.count(Feedback.id)).filter(Feedback.rating == i).scalar() or 0
            distribution[str(i)] = count
        
        return FeedbackStats(
            totalFeedback=total,
            averageRating=round(avg_rating, 2),
            ratingDistribution=distribution
        )
    except Exception as e:
        # Return empty stats if table doesn't exist yet
        print(f"[Feedback] Stats error: {e}")
        return FeedbackStats(
            totalFeedback=0,
            averageRating=0.0,
            ratingDistribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        )


@router.get("/all", response_model=List[FeedbackResponse])
def get_all_feedback(
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get all feedback from all users (public endpoint - no auth required).
    Shows latest feedback first.
    """
    try:
        feedback_list = (
            db.query(Feedback, User)
            .join(User, Feedback.user_id == User.id)
            .order_by(Feedback.created_at.desc())
            .limit(limit)
            .all()
        )
        
        result = []
        for feedback, user in feedback_list:
            data = feedback.to_dict()
            data["username"] = user.username
            result.append(FeedbackResponse(**data))
        
        return result
    except Exception as e:
        # Return empty list if table doesn't exist yet
        print(f"[Feedback] Get all error: {e}")
        return []


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit new feedback for the app.
    Requires authentication.
    
    - **rating**: Required rating from 1-5 stars
    - **category**: Optional category (general, feature, bug, improvement)
    - **review**: Optional written review
    """
    try:
        feedback = Feedback(
            user_id=current_user.id,
            rating=request.rating,
            category=request.category,
            review=request.review,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        response_data = feedback.to_dict()
        response_data["username"] = current_user.username
        return FeedbackResponse(**response_data)
    except Exception as e:
        db.rollback()
        print(f"[Feedback] Create error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating feedback: {str(e)}"
        )


@router.get("/", response_model=List[FeedbackResponse])
def get_user_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """
    Get current user's feedback history (requires auth).
    """
    try:
        feedback_list = (
            db.query(Feedback)
            .filter(Feedback.user_id == current_user.id)
            .order_by(Feedback.created_at.desc())
            .limit(limit)
            .all()
        )
        
        result = []
        for f in feedback_list:
            data = f.to_dict()
            data["username"] = current_user.username
            result.append(FeedbackResponse(**data))
        
        return result
    except Exception as e:
        print(f"[Feedback] Get user feedback error: {e}")
        return []


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a feedback entry (only if owned by current user).
    """
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found or not authorized"
        )
    
    db.delete(feedback)
    db.commit()
    return None
