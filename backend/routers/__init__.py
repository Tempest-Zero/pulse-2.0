# Routers Module
# FastAPI routers for PULSE API endpoints

from .tasks_router import router as tasks_router
from .schedule_router import router as schedule_router
from .reflections_router import router as reflections_router
from .mood_router import router as mood_router
from .extension_router import router as extension_router
from .auth_router import router as auth_router

__all__ = [
    "tasks_router",
    "schedule_router",
    "reflections_router",
    "mood_router",
    "extension_router",
    "auth_router",
]

