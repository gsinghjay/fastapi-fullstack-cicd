"""Test configuration and fixtures."""
import asyncio
import os
from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine, Generator
from typing import Any, cast

import psycopg2  # type: ignore
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pytest_docker.plugin import get_docker_ip, get_docker_services
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.security import create_access_token
from app.crud.user import create_user
from app.db.base import Base
from app.main import app as fastapi_app
from app.models.user import User as UserModel
from app.schemas.user import UserCreate

# Override settings for testing
os.environ["ENV_FILE"] = ".env.test"

# Test types
TEST_TYPES = ["unit", "integration", "regression"]


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    for test_type in TEST_TYPES:
        config.addinivalue_line(
            "markers", f"{test_type}: mark test as {test_type} test type"
        )


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Any) -> str:
    """Get the docker-compose.yml file path."""
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.test.yml")


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    """Get the docker compose project name."""
    return f"pytest{os.getpid()}"


@pytest.fixture(scope="session")
def docker_cleanup() -> list[str]:
    """Get the docker cleanup commands."""
    return ["down -v"]


@pytest.fixture(scope="session")
def docker_setup() -> list[str]:
    """Get the docker setup commands."""
    return ["up --build -d"]


@pytest.fixture(scope="session")
def docker_compose_command() -> str:
    """Get the docker compose command."""
    return "docker compose"


@pytest.fixture(scope="session")
def docker_ip() -> str:
    """Get the IP address to use for Docker containers."""
    return get_docker_ip()


def is_postgres_responsive(host: str, port: int) -> bool:
    """Check if PostgreSQL is responsive."""
    try:
        conn = psycopg2.connect(
            dbname="test",
            user="postgres",
            password="postgres",
            host=host,
            port=port,
        )
        conn.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def docker_services(
    docker_compose_file: str,
    docker_compose_project_name: str,
    docker_compose_command: str,
    docker_setup: list[str],
    docker_cleanup: list[str],
) -> Generator[Any, None, None]:
    """Start all services from docker-compose."""
    with get_docker_services(
        docker_compose_command,
        docker_compose_file,
        docker_compose_project_name=docker_compose_project_name,
        docker_setup=docker_setup,
        docker_cleanup=docker_cleanup,
    ) as services:
        yield services


@pytest.fixture(scope="session")
def postgres_service(docker_services: Any, docker_ip: str) -> str:
    """Ensure that PostgreSQL service is up and responsive."""
    port = docker_services.port_for("postgres", 5432)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_postgres_responsive(docker_ip, port)
    )
    return f"postgresql+asyncpg://postgres:postgres@{docker_ip}:{port}/test"


@pytest.fixture(scope="session")
def app(postgres_service: str) -> FastAPI:
    """Get the FastAPI application."""
    # Set the database URL for the app
    os.environ["DATABASE_URL"] = postgres_service
    return fastapi_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Return the backend to use for anyio."""
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine(postgres_service: str) -> AsyncGenerator[AsyncEngine, None]:
    """Create the test database engine."""
    engine = create_async_engine(
        postgres_service,
        echo=True,
        poolclass=NullPool,  # Use NullPool to ensure clean connections
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        # Drop tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Get a test database session.

    This fixture provides a database session for testing with automatic rollback.
    It uses a transaction that is rolled back after each test,
    ensuring test isolation.

    Args:
        test_engine: The test database engine.

    Yields:
        An async database session.
    """
    # Create a new session for each test
    testing_session_local = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with testing_session_local() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # The transaction will be rolled back when the session is closed


@pytest.fixture(scope="session")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Get a FastAPI test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client(
    app: FastAPI, test_engine: AsyncEngine
) -> AsyncGenerator[AsyncClient, None]:
    """Create an async client for testing."""
    # Cast the app to the expected ASGI application type
    asgi_callable = Callable[
        [
            dict[str, Any],
            Callable[[], Awaitable[dict[str, Any]]],
            Callable[[dict[str, Any]], Coroutine[None, None, None]],
        ],
        Coroutine[None, None, None],
    ]
    asgi_app = cast(asgi_callable, app)
    async with AsyncClient(
        transport=ASGITransport(app=asgi_app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def test_user_data() -> dict[str, Any]:
    """Get test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
    }


@pytest.fixture
async def test_user(
    db_session: AsyncSession, test_user_data: dict[str, Any]
) -> UserModel:
    """Create a test user."""
    user_in = UserCreate(**test_user_data)
    db_user = await create_user(db_session, user_in)
    await db_session.commit()
    return db_user


@pytest.fixture
def test_user_token(test_user: UserModel) -> str:
    """Get a test user token."""
    return create_access_token(subject=test_user.email)


@pytest.fixture
def auth_headers(test_user_token: str) -> dict[str, str]:
    """Get authentication headers."""
    return {"Authorization": f"Bearer {test_user_token}"}
