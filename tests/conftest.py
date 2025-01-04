from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

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


@pytest.fixture  # type: ignore[misc]
async def db_session() -> AsyncGenerator[AsyncSession, None]:
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


@pytest.fixture  # type: ignore[misc]
def client() -> Generator[TestClient, None, None]:
    """
    Fixture that provides a test client.

    Yields:
        TestClient: The test client.
    """
    with TestClient(app) as c:
        yield c
