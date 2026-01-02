import pytest
from typing import Generator
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.database.session import get_db
from app.models.user import User

# SQLITE_TEST_URL = "sqlite:///./test.db"
# engine = create_engine(
#     SQLITE_TEST_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=None
# )
SQLITE_TEST_URL = "sqlite:///"  # In-memory, no archivo
engine = create_engine(
    SQLITE_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_tables():
    SQLModel.metadata.create_all(engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        db.rollback()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    create_test_tables()


@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
