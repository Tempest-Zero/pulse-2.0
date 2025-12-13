"""
PULSE Backend API
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.base import init_db
from routers import tasks_router, schedule_router, reflections_router, mood_router

# Initialize database tables
init_db()

# Create FastAPI app
app = FastAPI(
    title="PULSE API",
    description="Backend API for PULSE - Your calm time coach",
    version="2.0.0",
)

import os

# CORS middleware for frontend
# Allow localhost for dev, and Railway domains for production
allowed_origins = [
    "http://localhost:3000",  # Next.js dev server
    "https://pulse-20-production.up.railway.app",  # Backend (self)
]

# Add frontend URL from environment if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# Also allow any Railway subdomain for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.up\.railway\.app",  # Allow any Railway subdomain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router)
app.include_router(schedule_router)
app.include_router(reflections_router)
app.include_router(mood_router)


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
    """Health check endpoint."""
    return {"status": "healthy"}
