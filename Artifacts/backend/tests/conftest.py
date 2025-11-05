"""Pytest fixtures for FastAPI endpoint tests.

This module configures an isolated in-memory SQLite database for
integration tests against the FastAPI application. Each test receives a
fresh SQLAlchemy engine bound to ``sqlite:///:memory:`` and the FastAPI
dependency that provides database sessions is overridden to ensure API
requests use the test database.

Key fixtures:

* ``engine`` – creates an in-memory SQLite engine with tables.
* ``session_factory`` – sessionmaker bound to the in-memory engine.
* ``db_session`` – convenient session for arranging test data.
* ``app`` – FastAPI application instance for tests.
* ``client`` – ``TestClient`` with the test database dependency override.
"""

from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.db.session import get_db
from app.main import create_app
from app.models import Base


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def engine():
    """Create a new in-memory SQLite engine for a test."""

    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def session_factory(engine) -> sessionmaker:
    """Return a sessionmaker bound to the in-memory engine."""

    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture
def db_session(session_factory: sessionmaker) -> Generator[Session, None, None]:
    """Provide a database session for arranging test data."""

    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def app(session_factory: sessionmaker) -> Generator[FastAPI, None, None]:
    """Create a FastAPI application with the test database override."""

    application = create_app()

    def _get_test_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    application.dependency_overrides[get_db] = _get_test_db
    try:
        yield application
    finally:
        application.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Yield a FastAPI TestClient that uses the in-memory database."""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def stub_password_hash(monkeypatch: pytest.MonkeyPatch):
    """Stub password hashing to avoid bcrypt backend differences during tests."""

    from app.core import security

    def fake_hash(password: str) -> str:
        return f"hashed-{password}"

    def fake_verify(plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed-{plain_password}"

    monkeypatch.setattr(security, "get_password_hash", fake_hash)
    monkeypatch.setattr(security, "verify_password", fake_verify)

