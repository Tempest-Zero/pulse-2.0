"""
Database Configuration
SQLAlchemy engine, session, and base model setup.
Supports SQLite (local dev), Railway PostgreSQL, and Supabase PostgreSQL.
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

def prepare_database_url(url: str) -> str:
    """
    Prepare DATABASE_URL for SQLAlchemy compatibility.
    - Converts postgres:// to postgresql:// (SQLAlchemy 2.0+ requirement)
    - Ensures sslmode=require for Supabase connections
    """
    if not url:
        return url

    # Fix URL scheme for SQLAlchemy 2.0+
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Parse URL to check/add SSL mode for Supabase
    parsed = urlparse(url)

    # Detect Supabase URLs (contain .supabase.co)
    is_supabase = parsed.hostname and "supabase" in parsed.hostname

    # Parse existing query params
    query_params = parse_qs(parsed.query) if parsed.query else {}

    # Add sslmode=require for Supabase if not already set
    if is_supabase and "sslmode" not in query_params:
        query_params["sslmode"] = ["require"]
        new_query = urlencode(query_params, doseq=True)
        parsed = parsed._replace(query=new_query)
        url = urlunparse(parsed)

    return url

# Prepare the DATABASE_URL
if DATABASE_URL:
    DATABASE_URL = prepare_database_url(DATABASE_URL)
    # Mask password in logs for security
    parsed = urlparse(DATABASE_URL)
    masked_host = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
    print(f"[DB] Using PostgreSQL: {parsed.scheme}://***@{masked_host}/{parsed.path.lstrip('/')}")
else:
    # Fall back to SQLite for local development
    DATABASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(DATABASE_DIR, exist_ok=True)
    DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'pulse.db')}"
    print(f"[DB] Using SQLite (local dev): {DATABASE_URL}")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific settings (local development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # PostgreSQL settings (Railway or Supabase)
    # Supabase uses connection pooling via PgBouncer, so we adjust settings
    is_supabase = "supabase" in DATABASE_URL

    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_pre_ping=True,      # Verify connections before using (important for external DBs)
        pool_size=5,             # Base pool size
        max_overflow=10,         # Allow up to 15 total connections
        pool_timeout=30,         # Wait up to 30s for a connection
        pool_recycle=300,        # Recycle connections after 5 minutes (Supabase timeout)
        echo=False,
        # Supabase-specific: shorter connect timeout
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"  # 30 second query timeout
        } if is_supabase else {}
    )

    if is_supabase:
        print("[DB] Supabase detected - using optimized connection settings")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Use with FastAPI's Depends() or as a context manager.
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
    # Log which tables will be created
    table_names = list(Base.metadata.tables.keys())
    print(f"[DB] Registered models: {table_names}")

    if not table_names:
        print("[DB] WARNING: No models registered! Check imports in main.py")
        return

    try:
        # Test connection first
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("[DB] Database connection successful")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print(f"[DB] init_db() complete - {len(table_names)} tables created/verified")

    except Exception as e:
        print(f"[DB] ERROR during init_db(): {e}")
        raise


def drop_db() -> None:
    """
    Drop all tables in the database.
    Use with caution - this deletes all data!
    """
    Base.metadata.drop_all(bind=engine)


def test_connection() -> bool:
    """
    Test database connectivity.
    Returns True if connection successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Connection test failed: {e}")
        return False
