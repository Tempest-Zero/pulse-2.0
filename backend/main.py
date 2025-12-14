"""
PULSE Backend API
FastAPI application entry point.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from models package (NOT models.base) to ensure all models are loaded
# before init_db() is called - otherwise Base.metadata won't know about any tables!
from models import init_db, test_connection
from routers import tasks_router, schedule_router, reflections_router, mood_router, ai_router, extension_router

# Track database status
db_initialized = False
db_error = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Database initialization happens here so the app can start even if DB fails.
    """
    global db_initialized, db_error
    
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
    
    print("[STARTUP] PULSE API ready to serve requests")
    
    yield  # App runs here
    
    # Shutdown
    print("[SHUTDOWN] PULSE API shutting down...")


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

# Combine environment origins with extension origins
all_origins = [o.strip() for o in env_origins] + [
    "chrome-extension://*",   # Chrome extension
    "moz-extension://*"       # Firefox extension
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router)
app.include_router(schedule_router)
app.include_router(reflections_router)
app.include_router(mood_router)
app.include_router(ai_router)
app.include_router(extension_router)


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
        "error": db_error if db_error else None
    }
