"""
Database Configuration
SQLAlchemy engine, session, and base model setup.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database configuration
# Use DATABASE_URL env var for production (Railway, Heroku, etc.)
# Falls back to SQLite for local development
DATABASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATABASE_DIR, exist_ok=True)

# Default SQLite URL for development
DEFAULT_DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'pulse.db')}"

# Get DATABASE_URL from environment (Railway provides this automatically)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Railway uses postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Determine if using SQLite (requires special connect_args)
is_sqlite = DATABASE_URL.startswith("sqlite")

# Create engine with appropriate settings
engine_kwargs = {
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true"
}

# SQLite requires check_same_thread=False for FastAPI
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Use with FastAPI's Depends() or as a context manager.
    
    Usage:
        with get_db() as db:
            # use db session
            
    Or with FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables in the database.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all tables in the database.
    Use with caution - this deletes all data!
    """
    Base.metadata.drop_all(bind=engine)
