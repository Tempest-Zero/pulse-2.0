"""
PULSE Backend API
FastAPI application entry point.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from models package (NOT models.base) to ensure all models are loaded
# before init_db() is called - otherwise Base.metadata won't know about any tables!
from models import init_db, test_connection
from routers import tasks_router, schedule_router, reflections_router, mood_router, ai_router, extension_router

# Initialize database tables
init_db()

# Create FastAPI app
app = FastAPI(
    title="PULSE API",
    description="Backend API for PULSE - Your calm time coach",
    version="2.0.0",
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
        "status": "running"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for Railway deployment.
    Verifies both API and database connectivity.
    """
    db_connected = test_connection()
    return {
        "status": "healthy" if db_connected else "degraded",
        "api": "ok",
        "database": "connected" if db_connected else "disconnected"
    }
