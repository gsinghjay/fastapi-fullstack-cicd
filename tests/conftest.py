import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Annotated

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base
from app.main import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine: AsyncEngine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestingSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> (
    Annotated[
        Generator[asyncio.AbstractEventLoop, None, None],
        "Create an instance of the default event loop for each test case",
    ]
):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db() -> (
    Annotated[AsyncGenerator[None, None], "Setup and teardown the test database"]
):
    """Create all tables for testing and clean up after tests."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> (
    Annotated[AsyncGenerator[AsyncSession, None], "Database session for testing"]
):
    """
    Fixture that provides a database session for tests.

    Yields:
        AsyncSession: The database session.
    """
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
def client() -> Annotated[Generator[TestClient, None, None], "FastAPI test client"]:
    """
    Fixture that provides a test client.

    Yields:
        TestClient: The test client.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
@pytest.mark.anyio
async def async_client() -> (
    Annotated[AsyncGenerator[AsyncClient, None], "FastAPI async test client"]
):
    """
    Fixture that provides an async client.

    Yields:
        AsyncClient: The async client.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
