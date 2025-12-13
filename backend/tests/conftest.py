"""
Shared fixtures and test configuration for PULSE Backend.
Sets up test database and provides common fixtures.
"""

import pytest
import os
import sys
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.base import Base, get_db
from main import app

# Test database configuration (SQLite for isolation)
TEST_DATABASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(TEST_DATABASE_DIR, exist_ok=True)
TEST_DATABASE_URL = f"sqlite:///{os.path.join(TEST_DATABASE_DIR, 'test.db')}"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Apply dependency override
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with fresh database."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_task(db_session):
    """Create a test task."""
    from models.task import Task
    
    task = Task(
        title="Test Task",
        duration=30,
        difficulty="medium",
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def test_schedule_block(db_session):
    """Create a test schedule block."""
    from models.schedule import ScheduleBlock
    
    block = ScheduleBlock(
        title="Test Block",
        start=9.0,
        duration=1.0,
        block_type="focus"
    )
    db_session.add(block)
    db_session.commit()
    db_session.refresh(block)
    return block


@pytest.fixture
def test_reflection(db_session):
    """Create a test reflection."""
    from models.reflection import Reflection
    
    reflection = Reflection(
        date=date.today(),
        mood_score=4,
        distractions=["phone", "email"],
        note="Test reflection note",
        completed_tasks=5,
        total_tasks=8
    )
    db_session.add(reflection)
    db_session.commit()
    db_session.refresh(reflection)
    return reflection


@pytest.fixture
def test_mood_entry(db_session):
    """Create a test mood entry."""
    from models.mood import MoodEntry
    
    entry = MoodEntry(mood="focused")
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry
