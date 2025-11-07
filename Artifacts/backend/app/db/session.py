"""
Database session management for the StaffAlloc application.

This module sets up the SQLAlchemy synchronous engine and session factory for the
SQLite database. It includes configuration for enabling Write-Ahead Logging (WAL)
mode to improve concurrency, which is crucial for a responsive local-first
application.

Key components:
- `engine`: The core SQLAlchemy synchronous engine connected to the database.
- `SessionLocal`: A factory for creating new database sessions.
- `get_db`: A FastAPI dependency to provide a database session to API endpoints,
  ensuring the session is properly closed after the request is handled.
- `create_db_and_tables`: A utility function to initialize the database schema,
  useful for initial setup or testing.
"""
import os
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models import Base  # Import Base from models

# The DATABASE_URL is taken from the central settings configuration.
# Using synchronous sqlite driver for simplicity in the prototype.
DATABASE_URL = settings.DATABASE_URL

# Create the SQLAlchemy synchronous engine.
# `echo=False` for production; set to True for debugging SQL queries.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)


# This event listener ensures that WAL (Write-Ahead Logging) mode is enabled
# every time a new connection is made to the SQLite database. WAL mode allows
# for concurrent reads and writes, which is essential for a responsive API
# and UI, especially when background jobs might be writing to the DB while
# the user is reading data.
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enables WAL mode for SQLite connections to improve concurrency.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout = 5000")  # 5 seconds
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


# Create a configured "Session" class.
# `autocommit=False` and `autoflush=False` are standard settings for using
# SQLAlchemy sessions with FastAPI.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides an SQLAlchemy database session.

    This function is a generator that yields a single database session
    per request. It uses a try/finally block to ensure that the session
    is always closed, even if an error occurs during the request.

    Yields:
        Session: The SQLAlchemy synchronous session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    """
    Utility function to create all database tables defined by the SQLAlchemy models.

    This function should be called once at application startup or via a CLI
    command. For production environments with existing data, Alembic migrations
    are the recommended approach for schema management.
    """
    # Ensure the directory for the database file exists
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # This will create all tables that inherit from the Base declarative class.
    Base.metadata.create_all(bind=engine)

    _run_sqlite_migrations()


def _run_sqlite_migrations() -> None:
    """Apply minimal SQLite migrations for newly added columns."""

    if engine.dialect.name != "sqlite":
        return

    def column_exists(conn, table: str, column: str) -> bool:
        result = conn.execute(text(f"PRAGMA table_info({table})"))
        return any(row[1] == column for row in result)

    with engine.begin() as conn:
        if not column_exists(conn, "users", "manager_id"):
            conn.execute(text("ALTER TABLE users ADD COLUMN manager_id INTEGER"))

        if not column_exists(conn, "roles", "owner_id"):
            conn.execute(text("ALTER TABLE roles ADD COLUMN owner_id INTEGER"))

        if not column_exists(conn, "lcats", "owner_id"):
            conn.execute(text("ALTER TABLE lcats ADD COLUMN owner_id INTEGER"))

        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_allocations_assignment ON allocations (project_assignment_id)"
            )
        )

