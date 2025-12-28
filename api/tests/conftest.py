import os
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config
from src.db.database import get_db
from src.main import app
from tests.test_helpers import AuthHelper

# Use a file-based SQLite database for testing to ensure persistence
# across connections within the same test session.
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """
    Fixture to set up and tear down the test database for the entire session.
    """
    # Ensure the old test database is gone before starting
    if os.path.exists("./test.db"):
        os.remove("./test.db")

    # Set the environment variable to signal test mode to env.py
    os.environ["TESTING"] = "1"

    from sqlalchemy import JSON
    from sqlalchemy.dialects import postgresql

    class SQLiteJSON(JSON):
        """SQLite-compatible mock for PostgreSQL's JSONB type."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            # Ignore any PostgreSQL-specific kwargs like astext_type
            kwargs.pop("astext_type", None)
            super().__init__(*args, **kwargs)

    postgresql.JSONB = SQLiteJSON

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)

    # Run migrations to create tables
    command.upgrade(alembic_cfg, "head")

    yield

    # Downgrade the database to clean up

    # Clean up the environment variable and the database file
    del os.environ["TESTING"]
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def auth_helper(client: TestClient) -> AuthHelper:
    """
    Provides a session-scoped AuthHelper instance with
    predefined users.
    """
    helper = AuthHelper(client)
    helper.setup_predefined_users()
    return helper
