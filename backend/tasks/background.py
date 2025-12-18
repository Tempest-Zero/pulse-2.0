"""
Background Tasks
Periodic tasks for application maintenance.
"""

import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from models.base import SessionLocal


def run_startup_tasks():
    """
    Tasks to run on application startup.
    
    - Create default user if needed
    """
    db = SessionLocal()
    try:
        from models.user import User
        
        # Ensure default user exists for single-user mode
        DEFAULT_USER_ID = 1
        default_user = db.query(User).filter(User.id == DEFAULT_USER_ID).first()
        if not default_user:
            default_user = User(id=DEFAULT_USER_ID, username="default_user")
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
    """
    print("[Shutdown] Shutdown tasks completed")


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
        while self._running:
            # Sleep for a minute
            await asyncio.sleep(60)
    
    def start(self):
        """Start the background task runner."""
        self._running = True
        print("[Background] Task runner started")
    
    def stop(self):
        """Stop the background task runner."""
        self._running = False
        if self._task:
            self._task.cancel()
        print("[Background] Task runner stopped")


# Global instance
background_runner = SimpleBackgroundRunner()

