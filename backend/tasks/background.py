"""
Background Tasks
Periodic tasks for AI model maintenance.
"""

import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from models.base import SessionLocal
from ai.agent import ScheduleAgent
from ai.implicit_feedback import ImplicitFeedbackInferencer


async def persist_agent_models_task():
    """
    Periodic task to persist all cached agent models.
    
    Should be scheduled to run every 5 minutes.
    """
    saved_count = ScheduleAgent.persist_all()
    if saved_count > 0:
        print(f"[Background] Persisted {saved_count} agent models")
    return saved_count


async def infer_pending_outcomes_task(min_age_hours: int = 2, limit: int = 100):
    """
    Periodic task to infer outcomes for old recommendations.
    
    Should be scheduled to run every 30 minutes.
    """
    db = SessionLocal()
    try:
        inferencer = ImplicitFeedbackInferencer()
        processed_count = inferencer.batch_infer_outcomes(db, min_age_hours, limit)
        if processed_count > 0:
            print(f"[Background] Inferred outcomes for {processed_count} recommendations")
        return processed_count
    finally:
        db.close()


def run_startup_tasks():
    """
    Tasks to run on application startup.
    
    - Create default user if needed
    - Load cached agents
    """
    db = SessionLocal()
    try:
        from models.user import User
        from ai.config import AIConfig
        
        # Ensure default user exists for single-user mode
        if AIConfig.SINGLE_USER_MODE:
            default_user = db.query(User).filter(User.id == AIConfig.DEFAULT_USER_ID).first()
            if not default_user:
                default_user = User(id=AIConfig.DEFAULT_USER_ID, username="default_user")
                db.add(default_user)
                db.commit()
                print("[Startup] Created default user")
    except Exception as e:
        print(f"[Startup] Warning during startup: {e}")
    finally:
        db.close()


def run_shutdown_tasks():
    """
    Tasks to run on application shutdown.
    
    - Persist all agent models
    """
    saved_count = ScheduleAgent.persist_all()
    print(f"[Shutdown] Saved {saved_count} agent models")


# Simple background task runner for development
# In production, use APScheduler or Celery
class SimpleBackgroundRunner:
    """
    Simple background task runner for development.
    
    For production, replace with APScheduler, Celery, or similar.
    """
    
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def _run_periodic_tasks(self):
        """Run periodic tasks in a loop."""
        persist_interval = 300  # 5 minutes
        infer_interval = 1800   # 30 minutes
        
        last_persist = datetime.now()
        last_infer = datetime.now()
        
        while self._running:
            now = datetime.now()
            
            # Check if persist is due
            if (now - last_persist).total_seconds() >= persist_interval:
                await persist_agent_models_task()
                last_persist = now
            
            # Check if infer is due
            if (now - last_infer).total_seconds() >= infer_interval:
                await infer_pending_outcomes_task()
                last_infer = now
            
            # Sleep for a minute
            await asyncio.sleep(60)
    
    def start(self):
        """Start the background task runner."""
        self._running = True
        # Note: This needs to be called from an async context
        # self._task = asyncio.create_task(self._run_periodic_tasks())
        print("[Background] Task runner started")
    
    def stop(self):
        """Stop the background task runner."""
        self._running = False
        if self._task:
            self._task.cancel()
        print("[Background] Task runner stopped")


# Global instance
background_runner = SimpleBackgroundRunner()
