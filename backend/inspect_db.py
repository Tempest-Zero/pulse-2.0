"""
Database Schema Inspector
Checks current database schema for migration planning.
"""
import sqlite3
import os

def inspect_db(db_path):
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"\n=== Database: {db_path} ===")
    print(f"Tables: {tables}")
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"\n{table}:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}){'  [PK]' if col[5] else ''}")
        
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")
    
    conn.close()

if __name__ == "__main__":
    inspect_db("data/pulse.db")
