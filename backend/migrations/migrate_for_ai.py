"""
AI Integration Migration Script
Adds missing columns to support the AI recommendation system.
"""
import sqlite3
import os
from datetime import datetime


def run_migration(db_path: str = "data/pulse.db"):
    """
    Migrate database schema to support AI module.
    
    Adds:
    - New columns to tasks table (user_id, priority, deadline, etc.)
    - New columns to mood_entries table (user_id, notes)
    - Default user if not exists
    """
    print(f"Starting migration for: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Ensure default user exists
        print("\n[1/4] Creating default user...")
        cursor.execute("SELECT id FROM users WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (id, username, created_at) VALUES (?, ?, ?)",
                (1, "default_user", datetime.now().isoformat())
            )
            print("  Created default user (id=1)")
        else:
            print("  Default user already exists")
        
        # Step 2: Add missing columns to tasks table
        print("\n[2/4] Adding columns to tasks table...")
        tasks_columns_to_add = [
            ("user_id", "INTEGER DEFAULT 1"),
            ("description", "TEXT"),
            ("estimated_duration", "INTEGER"),
            ("priority", "INTEGER DEFAULT 3"),
            ("deadline", "DATETIME"),
            ("status", "VARCHAR(20) DEFAULT 'pending'"),
            ("completed_at", "DATETIME"),
            ("is_deleted", "BOOLEAN DEFAULT 0"),
            ("is_archived", "BOOLEAN DEFAULT 0"),
        ]
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(tasks)")
        existing_cols = {col[1] for col in cursor.fetchall()}
        
        for col_name, col_type in tasks_columns_to_add:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
                print(f"  Added: tasks.{col_name}")
            else:
                print(f"  Exists: tasks.{col_name}")
        
        # Update status based on completed flag
        cursor.execute("""
            UPDATE tasks 
            SET status = CASE WHEN completed = 1 THEN 'completed' ELSE 'pending' END
            WHERE status IS NULL OR status = 'pending'
        """)
        
        # Step 3: Add missing columns to mood_entries table
        print("\n[3/4] Adding columns to mood_entries table...")
        mood_columns_to_add = [
            ("user_id", "INTEGER DEFAULT 1"),
            ("notes", "TEXT"),
        ]
        
        cursor.execute("PRAGMA table_info(mood_entries)")
        existing_cols = {col[1] for col in cursor.fetchall()}
        
        for col_name, col_type in mood_columns_to_add:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE mood_entries ADD COLUMN {col_name} {col_type}")
                print(f"  Added: mood_entries.{col_name}")
            else:
                print(f"  Exists: mood_entries.{col_name}")
        
        # Step 4: Update existing rows with default user_id
        print("\n[4/4] Setting default user_id for existing rows...")
        cursor.execute("UPDATE tasks SET user_id = 1 WHERE user_id IS NULL")
        tasks_updated = cursor.rowcount
        print(f"  Updated {tasks_updated} tasks")
        
        cursor.execute("UPDATE mood_entries SET user_id = 1 WHERE user_id IS NULL")
        moods_updated = cursor.rowcount
        print(f"  Updated {moods_updated} mood entries")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_migration(db_path: str = "data/pulse.db"):
    """Verify the migration was successful."""
    print("\n=== Verifying Migration ===")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tasks columns
    cursor.execute("PRAGMA table_info(tasks)")
    tasks_cols = [col[1] for col in cursor.fetchall()]
    required_tasks = ["user_id", "priority", "deadline", "status", "is_deleted", "is_archived"]
    missing_tasks = [c for c in required_tasks if c not in tasks_cols]
    
    # Check mood_entries columns
    cursor.execute("PRAGMA table_info(mood_entries)")
    mood_cols = [col[1] for col in cursor.fetchall()]
    required_moods = ["user_id", "notes"]
    missing_moods = [c for c in required_moods if c not in mood_cols]
    
    # Check default user
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = 1")
    has_default_user = cursor.fetchone()[0] > 0
    
    conn.close()
    
    print(f"Tasks columns: {len(tasks_cols)} columns")
    print(f"  Missing: {missing_tasks if missing_tasks else 'None'}")
    print(f"Mood columns: {len(mood_cols)} columns")
    print(f"  Missing: {missing_moods if missing_moods else 'None'}")
    print(f"Default user exists: {has_default_user}")
    
    if not missing_tasks and not missing_moods and has_default_user:
        print("\n✅ Migration verified - all columns present!")
        return True
    else:
        print("\n❌ Migration incomplete!")
        return False


if __name__ == "__main__":
    success = run_migration()
    if success:
        verify_migration()
