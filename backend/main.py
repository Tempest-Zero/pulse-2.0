"""
PULSE Backend API
FastAPI application entry point.
"""

# Load environment variables from .env FIRST (before any other imports)
from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from models package (NOT models.base) to ensure all models are loaded
# before init_db() is called - otherwise Base.metadata won't know about any tables!
from models import init_db, test_connection
from routers import tasks_router, schedule_router, reflections_router, mood_router, extension_router, auth_router

# Background tasks
from tasks.background import (
    run_startup_tasks,
    run_shutdown_tasks,
    background_runner,
)

# Track database status
db_initialized = False
db_error = None

# Track background task
_background_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Database initialization happens here so the app can start even if DB fails.
    """
    global db_initialized, db_error, _background_task
    
    print("[STARTUP] Initializing PULSE API...")
    
    # Try to initialize database (non-blocking - app starts even if this fails)
    try:
        init_db()
        db_initialized = True
        print("[STARTUP] Database initialized successfully")
    except Exception as e:
        db_error = str(e)
        db_initialized = False
        print(f"[STARTUP] WARNING: Database initialization failed: {e}")
        print("[STARTUP] App will continue without database - health check will show degraded status")
    
    # Run startup tasks (create default user, load cached agents)
    if db_initialized:
        try:
            run_startup_tasks()
            print("[STARTUP] Startup tasks completed")
        except Exception as e:
            print(f"[STARTUP] WARNING: Startup tasks failed: {e}")

        # Auto-seed if SEED_DATA environment variable is set
        if os.getenv("SEED_DATA", "").lower() in ("true", "1", "yes"):
            try:
                from seed_data import main as seed_main
                seed_main()
                print("[STARTUP] Database seeded with test data")
            except Exception as e:
                print(f"[STARTUP] WARNING: Seeding failed: {e}")
    
    # Start background task runner for periodic tasks
    # (model persistence every 5 min, outcome inference every 30 min)
    if db_initialized:
        try:
            background_runner._running = True
            _background_task = asyncio.create_task(background_runner._run_periodic_tasks())
            print("[STARTUP] Background task runner started")
        except Exception as e:
            print(f"[STARTUP] WARNING: Background runner failed to start: {e}")
    
    print("[STARTUP] PULSE API ready to serve requests")
    
    yield  # App runs here
    
    # Shutdown
    print("[SHUTDOWN] PULSE API shutting down...")
    
    # Stop background task runner
    if _background_task:
        background_runner._running = False
        _background_task.cancel()
        try:
            await _background_task
        except asyncio.CancelledError:
            pass
        print("[SHUTDOWN] Background task runner stopped")
    
    # Run shutdown tasks (persist all agent models)
    if db_initialized:
        try:
            run_shutdown_tasks()
            print("[SHUTDOWN] Shutdown tasks completed")
        except Exception as e:
            print(f"[SHUTDOWN] WARNING: Shutdown tasks failed: {e}")


# Create FastAPI app with lifespan
app = FastAPI(
    title="PULSE API",
    description="Backend API for PULSE - Your calm time coach",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware - origins from env var or defaults, plus extension support
default_origins = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173"
env_origins = os.getenv("CORS_ORIGINS", default_origins).split(",")

# Clean up environment origins
allowed_origins = [o.strip() for o in env_origins]

# Regex pattern for browser extensions (Chrome and Firefox)
# CORS wildcards like "chrome-extension://*" don't work, need regex instead
extension_regex = r"^(chrome-extension|moz-extension)://.*$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=extension_regex,  # Properly matches extension origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router)
app.include_router(schedule_router)
app.include_router(reflections_router)
app.include_router(mood_router)
# AI router removed
app.include_router(extension_router)
app.include_router(auth_router)


@app.get("/")
def root():
    """API health check."""
    return {
        "name": "PULSE API",
        "version": "2.0.0",
        "status": "running",
        "database": "connected" if db_initialized else "disconnected"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for Railway deployment.
    Verifies both API and database connectivity.
    """
    # Check live connection (not just init status)
    db_connected = test_connection() if db_initialized else False

    return {
        "status": "healthy" if db_connected else "degraded",
        "api": "ok",
        "database": "connected" if db_connected else "disconnected",
        "background_tasks": "running" if _background_task and not _background_task.done() else "stopped",
        "error": db_error if db_error else None
    }


@app.post("/dev/seed")
def seed_database():
    """
    Seed the database with test data.
    Creates a test user and sample data for development/testing.

    Test user credentials: test@pulse.app / password123
    """
    if not db_initialized:
        return {"success": False, "error": "Database not initialized"}

    try:
        from seed_data import main as seed_main
        seed_main()
        return {
            "success": True,
            "message": "Database seeded successfully",
            "test_user": {
                "email": "test@pulse.app",
                "password": "password123"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}