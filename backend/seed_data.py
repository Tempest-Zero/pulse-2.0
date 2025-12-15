"""
Seed Data Script
Populates the database with dummy user data for testing and development.

Usage:
    python seed_data.py

This creates:
- A test user (test@pulse.app / password123)
- Sample tasks with various priorities and statuses
- Sample mood entries over the past week
- Sample schedule blocks
- Sample reflections
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from models.base import SessionLocal, init_db
from models.user import User
from models.task import Task
from models.mood import MoodEntry
from models.schedule import ScheduleBlock
from models.reflection import Reflection
from core.auth import hash_password


# Test user credentials
TEST_USER = {
    "email": "test@pulse.app",
    "username": "testuser",
    "password": "password123",
}


def seed_user(db: Session) -> User:
    """Create or get the test user."""
    existing = db.query(User).filter(User.email == TEST_USER["email"]).first()
    if existing:
        print(f"[SEED] Test user already exists: {TEST_USER['email']}")
        return existing

    user = User(
        email=TEST_USER["email"],
        username=TEST_USER["username"],
        password_hash=hash_password(TEST_USER["password"]),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[SEED] Created test user: {TEST_USER['email']} / {TEST_USER['password']}")
    return user


def seed_tasks(db: Session, user_id: int) -> list[Task]:
    """Create sample tasks."""
    # Clear existing tasks for this user (optional - comment out to keep)
    # db.query(Task).filter(Task.user_id == user_id).delete()
    # db.commit()

    existing_count = db.query(Task).filter(Task.user_id == user_id).count()
    if existing_count > 0:
        print(f"[SEED] Tasks already exist for user ({existing_count} tasks)")
        return []

    now = datetime.now(timezone.utc)

    tasks_data = [
        # High priority - urgent tasks
        {
            "title": "Complete project proposal",
            "description": "Finish the Q1 project proposal and submit for review",
            "priority": 5,
            "status": "pending",
            "difficulty": "hard",
            "duration": 3.0,
            "estimated_duration": 180,
            "deadline": now + timedelta(days=2),
        },
        {
            "title": "Review pull requests",
            "description": "Review and approve pending PRs from the team",
            "priority": 4,
            "status": "in_progress",
            "difficulty": "medium",
            "duration": 1.0,
            "estimated_duration": 60,
            "deadline": now + timedelta(days=1),
        },
        # Medium priority - regular tasks
        {
            "title": "Update documentation",
            "description": "Update API documentation with new endpoints",
            "priority": 3,
            "status": "pending",
            "difficulty": "easy",
            "duration": 2.0,
            "estimated_duration": 120,
            "deadline": now + timedelta(days=5),
        },
        {
            "title": "Weekly team meeting prep",
            "description": "Prepare slides and agenda for weekly team meeting",
            "priority": 3,
            "status": "pending",
            "difficulty": "easy",
            "duration": 0.5,
            "estimated_duration": 30,
            "deadline": now + timedelta(days=3),
        },
        {
            "title": "Code refactoring",
            "description": "Refactor authentication module for better maintainability",
            "priority": 3,
            "status": "pending",
            "difficulty": "medium",
            "duration": 4.0,
            "estimated_duration": 240,
            "deadline": now + timedelta(days=7),
        },
        # Low priority - backlog items
        {
            "title": "Research new frameworks",
            "description": "Explore React Server Components and Next.js 14 features",
            "priority": 2,
            "status": "pending",
            "difficulty": "medium",
            "duration": 2.0,
            "estimated_duration": 120,
            "deadline": None,
        },
        {
            "title": "Write unit tests",
            "description": "Add unit tests for the task management module",
            "priority": 2,
            "status": "pending",
            "difficulty": "medium",
            "duration": 3.0,
            "estimated_duration": 180,
            "deadline": now + timedelta(days=14),
        },
        {
            "title": "Organize digital files",
            "description": "Clean up and organize project files and folders",
            "priority": 1,
            "status": "pending",
            "difficulty": "easy",
            "duration": 1.0,
            "estimated_duration": 60,
            "deadline": None,
        },
        # Completed tasks (for history)
        {
            "title": "Set up development environment",
            "description": "Configure local dev environment with all dependencies",
            "priority": 4,
            "status": "completed",
            "difficulty": "medium",
            "duration": 2.0,
            "estimated_duration": 120,
            "completed": True,
            "completed_at": now - timedelta(days=2),
        },
        {
            "title": "Database schema design",
            "description": "Design and implement initial database schema",
            "priority": 5,
            "status": "completed",
            "difficulty": "hard",
            "duration": 4.0,
            "estimated_duration": 240,
            "completed": True,
            "completed_at": now - timedelta(days=5),
        },
    ]

    tasks = []
    for data in tasks_data:
        task = Task(user_id=user_id, **data)
        db.add(task)
        tasks.append(task)

    db.commit()
    print(f"[SEED] Created {len(tasks)} sample tasks")
    return tasks


def seed_moods(db: Session, user_id: int) -> list[MoodEntry]:
    """Create sample mood entries for the past week."""
    existing_count = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).count()
    if existing_count > 0:
        print(f"[SEED] Mood entries already exist for user ({existing_count} entries)")
        return []

    now = datetime.now(timezone.utc)

    # Mood entries over the past week with realistic patterns
    moods_data = [
        # Today
        {"mood": "focused", "energy": 7, "notes": "Good morning, ready to tackle tasks!", "timestamp": now - timedelta(hours=2)},
        # Yesterday
        {"mood": "calm", "energy": 6, "notes": "Productive afternoon", "timestamp": now - timedelta(days=1, hours=4)},
        {"mood": "tired", "energy": 3, "notes": "Long day, need rest", "timestamp": now - timedelta(days=1, hours=10)},
        # 2 days ago
        {"mood": "energetic", "energy": 8, "notes": "Great start to the day!", "timestamp": now - timedelta(days=2, hours=1)},
        {"mood": "stressed", "energy": 4, "notes": "Deadline pressure", "timestamp": now - timedelta(days=2, hours=6)},
        # 3 days ago
        {"mood": "happy", "energy": 7, "notes": "Completed major milestone", "timestamp": now - timedelta(days=3, hours=3)},
        # 4 days ago
        {"mood": "neutral", "energy": 5, "notes": "Regular workday", "timestamp": now - timedelta(days=4, hours=2)},
        # 5 days ago
        {"mood": "anxious", "energy": 4, "notes": "Upcoming presentation", "timestamp": now - timedelta(days=5, hours=5)},
        {"mood": "relieved", "energy": 6, "notes": "Presentation went well!", "timestamp": now - timedelta(days=5, hours=8)},
        # 6 days ago
        {"mood": "motivated", "energy": 8, "notes": "New week, fresh start", "timestamp": now - timedelta(days=6, hours=1)},
    ]

    moods = []
    for data in moods_data:
        mood = MoodEntry(user_id=user_id, **data)
        db.add(mood)
        moods.append(mood)

    db.commit()
    print(f"[SEED] Created {len(moods)} sample mood entries")
    return moods


def seed_schedule(db: Session, user_id: int) -> list[ScheduleBlock]:
    """Create sample schedule blocks."""
    existing_count = db.query(ScheduleBlock).filter(ScheduleBlock.user_id == user_id).count()
    if existing_count > 0:
        print(f"[SEED] Schedule blocks already exist for user ({existing_count} blocks)")
        return []

    schedule_data = [
        # Morning routine
        {"title": "Morning Review", "start": 9.0, "duration": 0.5, "block_type": "routine"},
        {"title": "Deep Work Block", "start": 9.5, "duration": 2.0, "block_type": "focus"},
        # Midday
        {"title": "Lunch Break", "start": 12.0, "duration": 1.0, "block_type": "break"},
        {"title": "Team Standup", "start": 13.0, "duration": 0.5, "block_type": "meeting"},
        {"title": "Collaborative Work", "start": 13.5, "duration": 2.0, "block_type": "task"},
        # Afternoon
        {"title": "Break / Walk", "start": 15.5, "duration": 0.5, "block_type": "break"},
        {"title": "Email & Admin", "start": 16.0, "duration": 1.0, "block_type": "admin"},
        {"title": "Learning Time", "start": 17.0, "duration": 1.0, "block_type": "learning"},
        # Evening
        {"title": "Day Wrap-up", "start": 18.0, "duration": 0.5, "block_type": "routine"},
    ]

    blocks = []
    for data in schedule_data:
        block = ScheduleBlock(user_id=user_id, **data)
        db.add(block)
        blocks.append(block)

    db.commit()
    print(f"[SEED] Created {len(blocks)} sample schedule blocks")
    return blocks


def seed_reflections(db: Session, user_id: int) -> list[Reflection]:
    """Create sample reflections."""
    existing_count = db.query(Reflection).filter(Reflection.user_id == user_id).count()
    if existing_count > 0:
        print(f"[SEED] Reflections already exist for user ({existing_count} reflections)")
        return []

    now = datetime.now(timezone.utc)

    reflections_data = [
        {
            "content": "Today was productive! I managed to finish the API integration ahead of schedule. The key was breaking the task into smaller chunks and taking regular breaks.",
            "mood_score": 8,
            "productivity_score": 9,
            "reflection_type": "daily",
            "created_at": now - timedelta(days=1),
        },
        {
            "content": "Struggled with focus today. Too many interruptions from Slack. Need to set better boundaries and use Do Not Disturb mode during deep work sessions.",
            "mood_score": 5,
            "productivity_score": 4,
            "reflection_type": "daily",
            "created_at": now - timedelta(days=2),
        },
        {
            "content": "Great week overall! Completed 3 major tasks and learned a new framework. Areas to improve: better time estimation and saying no to scope creep.",
            "mood_score": 7,
            "productivity_score": 8,
            "reflection_type": "weekly",
            "created_at": now - timedelta(days=3),
        },
        {
            "content": "The morning routine is really helping. Waking up earlier and doing a quick review of tasks sets a positive tone for the whole day.",
            "mood_score": 8,
            "productivity_score": 7,
            "reflection_type": "daily",
            "created_at": now - timedelta(days=4),
        },
        {
            "content": "Need to work on task prioritization. Spent too much time on low-priority items while important deadlines approached.",
            "mood_score": 4,
            "productivity_score": 5,
            "reflection_type": "daily",
            "created_at": now - timedelta(days=5),
        },
    ]

    reflections = []
    for data in reflections_data:
        reflection = Reflection(user_id=user_id, **data)
        db.add(reflection)
        reflections.append(reflection)

    db.commit()
    print(f"[SEED] Created {len(reflections)} sample reflections")
    return reflections


def main():
    """Run the seed script."""
    print("\n" + "=" * 50)
    print("PULSE Database Seeder")
    print("=" * 50 + "\n")

    # Initialize database
    print("[SEED] Initializing database...")
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Seed data
        user = seed_user(db)
        seed_tasks(db, user.id)
        seed_moods(db, user.id)
        seed_schedule(db, user.id)
        seed_reflections(db, user.id)

        print("\n" + "=" * 50)
        print("Seeding Complete!")
        print("=" * 50)
        print(f"\nTest User Credentials:")
        print(f"  Email:    {TEST_USER['email']}")
        print(f"  Password: {TEST_USER['password']}")
        print("\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
