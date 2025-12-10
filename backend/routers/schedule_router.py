"""
Schedule Router
API endpoints for schedule block management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models.base import get_db
from models.schedule import ScheduleBlock
from schema.schedule import ScheduleBlockCreate, ScheduleBlockUpdate, ScheduleBlockResponse

router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.get("", response_model=List[ScheduleBlockResponse])
def get_blocks(
    block_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all schedule blocks.
    - Filter by block type (fixed, focus, break, task)
    """
    query = db.query(ScheduleBlock)
    
    if block_type:
        query = query.filter(ScheduleBlock.block_type == block_type)
    
    blocks = query.order_by(ScheduleBlock.start).all()
    return blocks


@router.post("", response_model=ScheduleBlockResponse, status_code=status.HTTP_201_CREATED)
def create_block(
    block_data: ScheduleBlockCreate,
    db: Session = Depends(get_db)
):
    """Create a new schedule block."""
    block = ScheduleBlock(
        title=block_data.title,
        start=block_data.start,
        duration=block_data.duration,
        block_type=block_data.block_type
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


@router.get("/range", response_model=List[ScheduleBlockResponse])
def get_blocks_in_range(
    start_hour: float = Query(..., ge=0, le=24),
    end_hour: float = Query(..., ge=0, le=24),
    db: Session = Depends(get_db)
):
    """Get all blocks that overlap with a time range."""
    blocks = db.query(ScheduleBlock).filter(
        ScheduleBlock.start < end_hour,
        (ScheduleBlock.start + ScheduleBlock.duration) > start_hour
    ).order_by(ScheduleBlock.start).all()
    
    return blocks


@router.get("/{block_id}", response_model=ScheduleBlockResponse)
def get_block(
    block_id: int,
    db: Session = Depends(get_db)
):
    """Get a single schedule block by ID."""
    block = db.query(ScheduleBlock).filter(ScheduleBlock.id == block_id).first()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule block not found"
        )
    
    return block


@router.patch("/{block_id}", response_model=ScheduleBlockResponse)
def update_block(
    block_id: int,
    block_data: ScheduleBlockUpdate,
    db: Session = Depends(get_db)
):
    """Update a schedule block's fields."""
    block = db.query(ScheduleBlock).filter(ScheduleBlock.id == block_id).first()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule block not found"
        )
    
    update_data = block_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(block, field, value)
    
    db.commit()
    db.refresh(block)
    return block


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(
    block_id: int,
    db: Session = Depends(get_db)
):
    """Delete a schedule block."""
    block = db.query(ScheduleBlock).filter(ScheduleBlock.id == block_id).first()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule block not found"
        )
    
    db.delete(block)
    db.commit()
    return


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_blocks(
    db: Session = Depends(get_db)
):
    """Clear all schedule blocks."""
    db.query(ScheduleBlock).delete()
    db.commit()
    return
