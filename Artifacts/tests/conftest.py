"""Pytest configuration and shared fixtures for the StaffAlloc backend tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"

# Ensure the backend package is importable as `app` when running tests.
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.main import app
from app.db.session import get_db
from app.models import Base


TEST_DB_PATH = Path("Artifacts/tests/test_staffalloc.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH.as_posix()}"

# Ensure the directory for the test database exists before creating the engine.
TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


def _override_get_db() -> Generator[Session, None, None]:
    """FastAPI dependency override that yields the synchronous testing session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient instance with an isolated database per test."""

    # Reset database schema for a clean slate before each test.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def db_session(client: TestClient) -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session bound to the testing database."""
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


@pytest.fixture(scope="session")
def api_prefix() -> str:
    """Helper fixture for the API base path."""
    return "/api/v1"


