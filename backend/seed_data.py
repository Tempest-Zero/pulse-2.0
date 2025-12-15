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
    # Valid moods: calm, energized, focused, tired, happy, stressed, anxious, sad, excited, overwhelmed, exhausted, neutral, content, okay
    moods_data = [
        # Today
        {"mood": "focused", "notes": "Good morning, ready to tackle tasks!", "timestamp": now - timedelta(hours=2)},
        # Yesterday
        {"mood": "calm", "notes": "Productive afternoon", "timestamp": now - timedelta(days=1, hours=4)},
        {"mood": "tired", "notes": "Long day, need rest", "timestamp": now - timedelta(days=1, hours=10)},
        # 2 days ago
        {"mood": "energized", "notes": "Great start to the day!", "timestamp": now - timedelta(days=2, hours=1)},
        {"mood": "stressed", "notes": "Deadline pressure", "timestamp": now - timedelta(days=2, hours=6)},
        # 3 days ago
        {"mood": "happy", "notes": "Completed major milestone", "timestamp": now - timedelta(days=3, hours=3)},
        # 4 days ago
        {"mood": "neutral", "notes": "Regular workday", "timestamp": now - timedelta(days=4, hours=2)},
        # 5 days ago
        {"mood": "anxious", "notes": "Upcoming presentation", "timestamp": now - timedelta(days=5, hours=5)},
        {"mood": "content", "notes": "Presentation went well!", "timestamp": now - timedelta(days=5, hours=8)},
        # 6 days ago
        {"mood": "excited", "notes": "New week, fresh start", "timestamp": now - timedelta(days=6, hours=1)},
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
    # ScheduleBlock doesn't have user_id - it's global
    existing_count = db.query(ScheduleBlock).count()
    if existing_count > 0:
        print(f"[SEED] Schedule blocks already exist ({existing_count} blocks)")
        return []

    # Valid block_type values: 'fixed', 'focus', 'break', 'task'
    schedule_data = [
        # Morning routine
        {"title": "Morning Review", "start": 9.0, "duration": 0.5, "block_type": "fixed"},
        {"title": "Deep Work Block", "start": 9.5, "duration": 2.0, "block_type": "focus"},
        # Midday
        {"title": "Lunch Break", "start": 12.0, "duration": 1.0, "block_type": "break"},
        {"title": "Team Standup", "start": 13.0, "duration": 0.5, "block_type": "fixed"},
        {"title": "Collaborative Work", "start": 13.5, "duration": 2.0, "block_type": "task"},
        # Afternoon
        {"title": "Break / Walk", "start": 15.5, "duration": 0.5, "block_type": "break"},
        {"title": "Email & Admin", "start": 16.0, "duration": 1.0, "block_type": "task"},
        {"title": "Learning Time", "start": 17.0, "duration": 1.0, "block_type": "focus"},
        # Evening
        {"title": "Day Wrap-up", "start": 18.0, "duration": 0.5, "block_type": "fixed"},
    ]

    blocks = []
    for data in schedule_data:
        block = ScheduleBlock(**data)
        db.add(block)
        blocks.append(block)

    db.commit()
    print(f"[SEED] Created {len(blocks)} sample schedule blocks")
    return blocks


def seed_reflections(db: Session, user_id: int) -> list[Reflection]:
    """Create sample reflections."""
    # Reflections use date as unique key, not user_id
    existing_count = db.query(Reflection).count()
    if existing_count > 0:
        print(f"[SEED] Reflections already exist ({existing_count} reflections)")
        return []

    today = datetime.now(timezone.utc).date()

    # Reflection model fields: date, mood_score (1-5), distractions, note, completed_tasks, total_tasks
    reflections_data = [
        {
            "date": today - timedelta(days=1),
            "mood_score": 4,  # 1-5 scale (4 = energized)
            "note": "Today was productive! I managed to finish the API integration ahead of schedule. The key was breaking the task into smaller chunks and taking regular breaks.",
            "distractions": ["social_media", "notifications"],
            "completed_tasks": 5,
            "total_tasks": 6,
        },
        {
            "date": today - timedelta(days=2),
            "mood_score": 2,  # 1-5 scale (2 = tired)
            "note": "Struggled with focus today. Too many interruptions from Slack. Need to set better boundaries and use Do Not Disturb mode during deep work sessions.",
            "distractions": ["meetings", "slack", "emails"],
            "completed_tasks": 2,
            "total_tasks": 5,
        },
        {
            "date": today - timedelta(days=3),
            "mood_score": 4,
            "note": "Great progress! Completed 3 major tasks and learned a new framework. Areas to improve: better time estimation.",
            "distractions": ["youtube"],
            "completed_tasks": 4,
            "total_tasks": 4,
        },
        {
            "date": today - timedelta(days=4),
            "mood_score": 5,  # 1-5 scale (5 = very energized)
            "note": "The morning routine is really helping. Waking up earlier and doing a quick review of tasks sets a positive tone for the whole day.",
            "distractions": [],
            "completed_tasks": 6,
            "total_tasks": 6,
        },
        {
            "date": today - timedelta(days=5),
            "mood_score": 2,
            "note": "Need to work on task prioritization. Spent too much time on low-priority items while important deadlines approached.",
            "distractions": ["procrastination", "social_media"],
            "completed_tasks": 1,
            "total_tasks": 4,
        },
    ]

    reflections = []
    for data in reflections_data:
        reflection = Reflection(**data)
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
