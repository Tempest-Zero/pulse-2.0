"""
Database Configuration
SQLAlchemy engine, session, and base model setup.
Supports both SQLite (development) and PostgreSQL (production via DATABASE_URL).
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os

# Get DATABASE_URL from environment (Railway sets this automatically)
DATABASE_URL = os.getenv("DATABASE_URL")

# Handle Railway's postgres:// vs postgresql:// URL scheme
# SQLAlchemy 2.0+ requires postgresql:// not postgres://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fall back to SQLite for local development if no DATABASE_URL
if not DATABASE_URL:
    DATABASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(DATABASE_DIR, exist_ok=True)
    DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'pulse.db')}"
    print(f"[DB] Using SQLite (local dev): {DATABASE_URL}")
else:
    # Mask password in logs for security
    masked_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"[DB] Using PostgreSQL: ...@{masked_url}")

# Create engine with appropriate settings for SQLite vs PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # PostgreSQL settings (no check_same_thread needed)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10,
        echo=False
    )

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
