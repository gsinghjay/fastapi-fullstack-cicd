# Quality Assurance Guide

This guide provides comprehensive information about testing practices, tools, and guidelines for the FastAPI Full-Stack CI/CD Template.

## Table of Contents

- [Testing Strategy](#testing-strategy)
- [Test Types](#test-types)
- [Database Testing](#database-testing)
- [API Testing](#api-testing)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [CI/CD Integration](#cicd-integration)
- [SQLAlchemy Model Testing](#sqlalchemy-model-testing)

## Testing Strategy

### Test Pyramid
Our testing strategy follows the test pyramid approach:
1. Unit Tests (70%)
2. Integration Tests (20%)
3. End-to-End Tests (10%)

### Test Environment
- Development: Local environment with SQLite
- Testing: Docker-based PostgreSQL
- Staging: Replicated production environment
- Production: Live environment

## Test Types

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic
- Example:
```python
def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)
```

### Integration Tests
- Test component interactions
- Use test database
- Test API endpoints
- Example:
```python
@pytest.mark.integration
async def test_user_workflow(async_client: AsyncClient):
    # Create user
    response = await async_client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Login
    response = await async_client.post("/api/v1/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Get user profile
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### End-to-End Tests
- Test complete user workflows
- Use staging environment
- Test UI interactions (if applicable)
- Example:
```python
@pytest.mark.e2e
async def test_complete_user_journey(async_client: AsyncClient):
    # Register
    # Login
    # Update Profile
    # Perform Actions
    # Logout
    pass
```

## Database Testing

### Test Database Setup
```python
@pytest.fixture(scope="session")
async def test_engine(postgres_service: str) -> AsyncGenerator[AsyncEngine, None]:
    """Create the test database engine."""
    engine = create_async_engine(
        postgres_service,
        echo=True,
        poolclass=NullPool
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
```

### Session Management
```python
@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session with automatic rollback."""
    testing_session_local = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with testing_session_local() as session:
        async with session.begin():
            yield session
```

### Database Operations Testing
```python
@pytest.mark.integration
async def test_crud_operations(db_session: AsyncSession):
    # Create
    user = User(email="test@example.com", hashed_password="hash")
    db_session.add(user)
    await db_session.commit()

    # Read
    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    db_user = result.scalar_one()
    assert db_user.email == "test@example.com"

    # Update
    db_user.full_name = "Updated Name"
    await db_session.commit()

    # Delete
    await db_session.delete(db_user)
    await db_session.commit()
```

## API Testing

### FastAPI TestClient Setup
```python
@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### API Endpoint Testing
```python
async def test_api_endpoints(async_client: AsyncClient):
    # Test GET endpoint
    response = await async_client.get("/api/v1/users")
    assert response.status_code == 200

    # Test POST endpoint
    response = await async_client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "password": "test"}
    )
    assert response.status_code == 201

    # Test authentication
    response = await async_client.get(
        "/api/v1/protected",
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
```

## Performance Testing

### Load Testing
Using [k6](https://k6.io/) for load testing:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '30s',
};

export default function () {
    const res = http.get('http://test.host/api/v1/health');
    check(res, { 'status was 200': (r) => r.status == 200 });
    sleep(1);
}
```

### Database Performance
```python
async def test_bulk_operations(db_session: AsyncSession):
    # Test bulk insert
    users = [
        User(email=f"user{i}@example.com", hashed_password="hash")
        for i in range(1000)
    ]
    db_session.add_all(users)
    await db_session.commit()

    # Test bulk select
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 1000
```

## Security Testing

### Authentication Testing
```python
async def test_auth_flow(async_client: AsyncClient):
    # Test invalid login
    response = await async_client.post(
        "/api/v1/login",
        data={"username": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == 401

    # Test valid login
    response = await async_client.post(
        "/api/v1/login",
        data={"username": "test@example.com", "password": "correct"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Authorization Testing
```python
async def test_permissions(async_client: AsyncClient):
    # Test unauthorized access
    response = await async_client.get("/api/v1/admin")
    assert response.status_code == 401

    # Test forbidden access
    response = await async_client.get(
        "/api/v1/admin",
        headers={"Authorization": "Bearer user_token"}
    )
    assert response.status_code == 403

    # Test authorized access
    response = await async_client.get(
        "/api/v1/admin",
        headers={"Authorization": "Bearer admin_token"}
    )
    assert response.status_code == 200
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install Poetry
      uses: snok/install-poetry@v1

    - name: Install dependencies
      run: poetry install

    - name: Run tests
      run: poetry run pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### Test Coverage Requirements
- Minimum coverage: 80%
- Critical paths: 100%
- New code: 90%

### Continuous Testing
- Pre-commit hooks for local testing
- Automated tests on PR
- Nightly full test suite
- Performance benchmarks

Remember to:
- Keep tests focused and independent
- Use appropriate fixtures and mocks
- Follow AAA (Arrange-Act-Assert) pattern
- Document test requirements and setup
- Monitor test execution times
- Regularly review and update tests

## Docker Integration Testing

### pytest-docker Setup
```python
@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Any) -> str:
    """Get the docker-compose.yml file path."""
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.test.yml")

@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    """Get the docker compose project name."""
    return f"pytest{os.getpid()}"

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
```

### Service Health Checks
```python
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
def postgres_service(docker_services: Any, docker_ip: str) -> str:
    """Ensure that PostgreSQL service is up and responsive."""
    port = docker_services.port_for("postgres", 5432)
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_postgres_responsive(docker_ip, port)
    )
    return f"postgresql+asyncpg://postgres:postgres@{docker_ip}:{port}/test"
```

### Docker Compose Configuration
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test
    ports:
      - "5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Container Management
```python
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
```

### Testing Multiple Services
```python
@pytest.fixture(scope="session")
def redis_service(docker_services: Any, docker_ip: str) -> str:
    """Ensure that Redis service is up and responsive."""
    port = docker_services.port_for("redis", 6379)
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_redis_responsive(docker_ip, port)
    )
    return f"redis://{docker_ip}:{port}/0"

def is_redis_responsive(host: str, port: int) -> bool:
    """Check if Redis is responsive."""
    try:
        import redis
        client = redis.Redis(host=host, port=port)
        return client.ping()
    except Exception:
        return False
```

### Integration Test Examples

#### Testing Database Migrations
```python
@pytest.mark.integration
async def test_migrations(postgres_service: str):
    """Test database migrations."""
    from alembic.config import Config
    from alembic import command

    # Create Alembic config
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_service)

    try:
        # Run migrations
        command.upgrade(alembic_cfg, "head")

        # Verify migrations
        command.check(alembic_cfg)

        # Test downgrade
        command.downgrade(alembic_cfg, "-1")
        command.upgrade(alembic_cfg, "+1")
    except Exception as e:
        pytest.fail(f"Migration failed: {e}")
```

#### Testing Service Dependencies
```python
@pytest.mark.integration
async def test_service_interaction(
    postgres_service: str,
    redis_service: str,
    async_client: AsyncClient
):
    """Test interaction between services."""
    # Create user in database
    response = await async_client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Verify cache in Redis
    import redis.asyncio as redis
    redis_client = redis.from_url(redis_service)
    cached_user = await redis_client.get(f"user:{user_id}")
    assert cached_user is not None
```

### Best Practices for Docker Testing

1. **Resource Management**:
   - Use appropriate container resources
   - Clean up containers after tests
   - Handle container logs
   ```python
   @pytest.fixture(scope="session", autouse=True)
   def cleanup_docker_logs(docker_services: Any):
       """Clean up docker logs after tests."""
       yield
       for service in docker_services.services:
           logs = docker_services.logs(service)
           print(f"\nLogs for {service}:")
           print(logs.decode())
   ```

2. **Network Management**:
   - Handle service discovery
   - Manage port allocation
   - Handle network failures
   ```python
   @pytest.fixture(scope="session")
   def docker_network() -> str:
       """Get the docker network name."""
       return f"test-network-{os.getpid()}"
   ```

3. **Volume Management**:
   - Handle persistent data
   - Clean up volumes
   - Manage test data
   ```python
   @pytest.fixture(scope="session")
   def docker_volumes() -> list[str]:
       """Get the docker volume names."""
       return [
           f"postgres-data-{os.getpid()}",
           f"redis-data-{os.getpid()}"
       ]
   ```

4. **Security Considerations**:
   - Use non-root users
   - Secure sensitive data
   - Handle credentials
   ```python
   @pytest.fixture(scope="session")
   def docker_environment() -> dict[str, str]:
       """Get secure environment variables."""
       return {
           "POSTGRES_USER": "test_user",
           "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
           "POSTGRES_DB": "test_db"
       }
   ```

5. **Performance Optimization**:
   - Reuse containers when possible
   - Optimize build context
   - Use multi-stage builds
   ```dockerfile
   # Dockerfile.test
   FROM python:3.11-slim as builder

   WORKDIR /app
   COPY pyproject.toml poetry.lock ./
   RUN pip install poetry && \
       poetry config virtualenvs.create false && \
       poetry install --no-dev

   FROM python:3.11-slim
   WORKDIR /app
   COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
   COPY . .
   ```

Remember to:
- Use appropriate fixture scopes
- Handle service dependencies
- Implement proper health checks
- Clean up resources
- Monitor container performance
- Log container output for debugging
- Handle network and volume management
- Follow security best practices

## FastAPI-Specific Testing

### Testing Response Models
```python
from fastapi.testclient import TestClient
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

async def test_response_model(async_client: AsyncClient):
    """Test response model validation."""
    response = await async_client.get("/api/v1/users/1")
    assert response.status_code == 200

    # Validate response matches model
    user = UserResponse.model_validate(response.json())
    assert isinstance(user.id, int)
    assert isinstance(user.email, str)
    assert isinstance(user.is_active, bool)
```

### Testing Request Validation
```python
async def test_request_validation(async_client: AsyncClient):
    """Test request validation."""
    # Test invalid email format
    response = await async_client.post(
        "/api/v1/users/",
        json={"email": "invalid-email", "password": "test"}
    )
    assert response.status_code == 422

    # Test missing required field
    response = await async_client.post(
        "/api/v1/users/",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 422

    # Test invalid password length
    response = await async_client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "short"}
    )
    assert response.status_code == 422
```

### Testing Custom Response Classes
```python
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse

async def test_custom_responses(async_client: AsyncClient):
    """Test different response types."""
    # Test JSON response
    response = await async_client.get("/api/v1/data")
    assert response.headers["content-type"] == "application/json"

    # Test HTML response
    response = await async_client.get("/api/v1/docs/html")
    assert response.headers["content-type"] == "text/html; charset=utf-8"

    # Test streaming response
    response = await async_client.get("/api/v1/stream")
    assert response.headers["content-type"] == "application/octet-stream"
```

### Testing Background Tasks
```python
from fastapi import BackgroundTasks

async def test_background_tasks(async_client: AsyncClient, mocker):
    """Test background task execution."""
    # Mock background task
    mock_task = mocker.patch("app.tasks.process_data")

    response = await async_client.post(
        "/api/v1/process",
        json={"data": "test"}
    )
    assert response.status_code == 202

    # Verify task was queued
    mock_task.assert_called_once_with("test")
```

### Testing WebSocket Endpoints
```python
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

def test_websocket(client: TestClient):
    """Test WebSocket connection and messages."""
    with client.websocket_connect("/ws") as websocket:
        # Test connection
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Test sending message
        websocket.send_json({"message": "hello"})
        data = websocket.receive_json()
        assert data["message"] == "echo: hello"

        # Test close connection
        websocket.close()
```

### Testing Middleware
```python
async def test_middleware(async_client: AsyncClient):
    """Test custom middleware."""
    # Test CORS headers
    response = await async_client.get(
        "/api/v1/users",
        headers={"Origin": "http://testserver"}
    )
    assert response.headers["access-control-allow-origin"]

    # Test custom headers
    response = await async_client.get("/api/v1/users")
    assert response.headers["x-custom-header"] == "value"

    # Test rate limiting
    for _ in range(5):
        await async_client.get("/api/v1/users")
    response = await async_client.get("/api/v1/users")
    assert response.status_code == 429
```

### Testing Dependencies
```python
from fastapi import Depends, HTTPException
from unittest.mock import AsyncMock

async def test_dependency_override(async_client: AsyncClient, mocker):
    """Test dependency overrides."""
    # Mock dependency
    async def mock_get_current_user():
        return {"id": 1, "email": "test@example.com"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    # Clean up
    app.dependency_overrides.clear()
```

### Testing Exception Handlers
```python
async def test_exception_handlers(async_client: AsyncClient):
    """Test custom exception handlers."""
    # Test 404 handler
    response = await async_client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"

    # Test custom exception
    response = await async_client.post("/api/v1/users/validate")
    assert response.status_code == 400
    assert "validation_error" in response.json()

    # Test 500 handler
    response = await async_client.get("/api/v1/error")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
```

### Testing Static Files
```python
async def test_static_files(async_client: AsyncClient):
    """Test static file serving."""
    # Test CSS file
    response = await async_client.get("/static/css/style.css")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/css; charset=utf-8"

    # Test image file
    response = await async_client.get("/static/img/logo.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    # Test file not found
    response = await async_client.get("/static/nonexistent.file")
    assert response.status_code == 404
```

### Testing Form Data and File Uploads
```python
import io
from fastapi import File, UploadFile

async def test_file_upload(async_client: AsyncClient):
    """Test file upload handling."""
    # Create test file
    file_content = b"test file content"
    file = io.BytesIO(file_content)

    # Test single file upload
    response = await async_client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", file, "text/plain")}
    )
    assert response.status_code == 200

    # Test multiple files
    files = {
        "file1": ("test1.txt", io.BytesIO(b"content1"), "text/plain"),
        "file2": ("test2.txt", io.BytesIO(b"content2"), "text/plain")
    }
    response = await async_client.post("/api/v1/upload-multiple", files=files)
    assert response.status_code == 200
```

### Testing OpenAPI Schema
```python
def test_openapi_schema(client: TestClient):
    """Test OpenAPI schema generation."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Verify basic schema structure
    assert schema["openapi"] == "3.1.0"
    assert schema["info"]["title"] == "FastAPI App"
    assert "paths" in schema

    # Verify specific endpoint schema
    user_path = schema["paths"]["/api/v1/users"]["post"]
    assert "requestBody" in user_path
    assert "responses" in user_path

    # Verify security schemes
    assert "securitySchemes" in schema["components"]
    assert "OAuth2PasswordBearer" in schema["components"]["securitySchemes"]
```

Remember to:
- Test all response types and status codes
- Validate request and response models
- Test middleware functionality
- Handle file uploads properly
- Verify OpenAPI schema accuracy
- Test WebSocket connections
- Validate exception handling
- Check static file serving
- Test form data processing
- Verify security mechanisms

## SQLAlchemy Model Testing

### Testing User Model
```python
import uuid
from sqlalchemy import select
from app.models.user import User

@pytest.mark.asyncio
async def test_user_model_creation(db_session: AsyncSession):
    """Test User model creation and attributes."""
    # Create test user
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()

    # Verify UUID generation
    assert isinstance(user.id, uuid.UUID)

    # Test unique constraint
    duplicate_user = User(
        email="test@example.com",  # Same email
        full_name="Another User",
        hashed_password="different_password"
    )
    db_session.add(duplicate_user)
    with pytest.raises(Exception):  # SQLAlchemy will raise on unique constraint violation
        await db_session.commit()

@pytest.mark.asyncio
async def test_user_model_queries(db_session: AsyncSession):
    """Test User model queries."""
    # Create test users
    users = [
        User(
            email=f"user{i}@example.com",
            full_name=f"User {i}",
            hashed_password=f"password{i}",
            is_active=True,
            is_superuser=i == 0  # First user is superuser
        )
        for i in range(3)
    ]
    db_session.add_all(users)
    await db_session.commit()

    # Test select by email
    result = await db_session.execute(
        select(User).where(User.email == "user0@example.com")
    )
    user = result.scalar_one()
    assert user.full_name == "User 0"
    assert user.is_superuser is True

    # Test select active users
    result = await db_session.execute(
        select(User).where(User.is_active == True)  # noqa: E712
    )
    active_users = result.scalars().all()
    assert len(active_users) == 3

    # Test select superusers
    result = await db_session.execute(
        select(User).where(User.is_superuser == True)  # noqa: E712
    )
    superusers = result.scalars().all()
    assert len(superusers) == 1

@pytest.mark.asyncio
async def test_user_model_updates(db_session: AsyncSession):
    """Test User model updates."""
    # Create test user
    user = User(
        email="update@example.com",
        full_name="Update User",
        hashed_password="original_password",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    # Update user fields
    user.full_name = "Updated Name"
    user.is_active = False
    await db_session.commit()

    # Verify updates
    result = await db_session.execute(
        select(User).where(User.email == "update@example.com")
    )
    updated_user = result.scalar_one()
    assert updated_user.full_name == "Updated Name"
    assert updated_user.is_active is False

@pytest.mark.asyncio
async def test_user_model_deletion(db_session: AsyncSession):
    """Test User model deletion."""
    # Create test user
    user = User(
        email="delete@example.com",
        full_name="Delete User",
        hashed_password="delete_password"
    )
    db_session.add(user)
    await db_session.commit()

    # Delete user
    await db_session.delete(user)
    await db_session.commit()

    # Verify deletion
    result = await db_session.execute(
        select(User).where(User.email == "delete@example.com")
    )
    assert result.first() is None

@pytest.mark.asyncio
async def test_user_model_validation(db_session: AsyncSession):
    """Test User model validation."""
    # Test required fields
    with pytest.raises(Exception):
        user = User(
            email="missing@example.com"
            # Missing required fields: full_name, hashed_password
        )
        db_session.add(user)
        await db_session.commit()

    # Test field length constraints
    with pytest.raises(Exception):
        user = User(
            email="a" * 256 + "@example.com",  # Exceeds String(255)
            full_name="Test User",
            hashed_password="password"
        )
        db_session.add(user)
        await db_session.commit()

@pytest.mark.asyncio
async def test_user_model_defaults(db_session: AsyncSession):
    """Test User model default values."""
    user = User(
        email="defaults@example.com",
        full_name="Default User",
        hashed_password="password"
    )
    db_session.add(user)
    await db_session.commit()

    # Test default values
    assert user.is_active is True  # Default from model
    assert user.is_superuser is False  # Default from model
    assert user.id is not None  # UUID should be auto-generated

@pytest.mark.asyncio
async def test_user_model_relationships():
    """
    Test User model relationships.
    Add this test when implementing relationships with other models.
    """
    pass  # TODO: Implement when adding relationships

### Model Testing Best Practices

1. **Test Data Management**:
   - Use factories for test data creation
   - Clean up test data after each test
   - Use meaningful test data values
   ```python
   @pytest.fixture
   def user_factory(db_session: AsyncSession):
       """Factory for creating test users."""
       async def create_user(**kwargs):
           user = User(
               email=kwargs.get("email", "test@example.com"),
               full_name=kwargs.get("full_name", "Test User"),
               hashed_password=kwargs.get("hashed_password", "password"),
               is_active=kwargs.get("is_active", True),
               is_superuser=kwargs.get("is_superuser", False)
           )
           db_session.add(user)
           await db_session.commit()
           return user
       return create_user
   ```

2. **Constraint Testing**:
   - Test unique constraints
   - Test nullable constraints
   - Test length constraints
   ```python
   @pytest.mark.asyncio
   async def test_user_constraints(db_session: AsyncSession):
       """Test database constraints."""
       # Test unique email constraint
       user1 = User(email="same@example.com", full_name="User 1", hashed_password="pass1")
       user2 = User(email="same@example.com", full_name="User 2", hashed_password="pass2")
       db_session.add(user1)
       await db_session.commit()
       db_session.add(user2)
       with pytest.raises(Exception):
           await db_session.commit()
   ```

3. **Index Testing**:
   - Verify index effectiveness
   - Test query performance
   ```python
   @pytest.mark.asyncio
   async def test_user_indexes(db_session: AsyncSession):
       """Test index usage in queries."""
       # Create many users
       users = [
           User(
               email=f"user{i}@example.com",
               full_name=f"User {i}",
               hashed_password=f"pass{i}"
           )
           for i in range(1000)
       ]
       db_session.add_all(users)
       await db_session.commit()

       # Test indexed query performance
       start_time = time.time()
       result = await db_session.execute(
           select(User).where(User.email == "user500@example.com")
       )
       query_time = time.time() - start_time
       assert query_time < 0.1  # Query should be fast due to index
   ```

4. **Bulk Operations**:
   - Test bulk inserts
   - Test bulk updates
   - Test bulk deletes
   ```python
   @pytest.mark.asyncio
   async def test_user_bulk_operations(db_session: AsyncSession):
       """Test bulk operations."""
       # Bulk insert
       users = [
           User(
               email=f"bulk{i}@example.com",
               full_name=f"Bulk User {i}",
               hashed_password="bulk_pass"
           )
           for i in range(100)
       ]
       db_session.add_all(users)
       await db_session.commit()

       # Bulk update
       await db_session.execute(
           update(User)
           .where(User.email.like("bulk%"))
           .values(is_active=False)
       )
       await db_session.commit()

       # Verify bulk update
       result = await db_session.execute(
           select(User).where(User.is_active == False)  # noqa: E712
       )
       assert len(result.scalars().all()) == 100
   ```

Remember to:
- Test all model constraints
- Verify default values
- Test field validations
- Check index effectiveness
- Test bulk operations
- Verify relationship behavior
- Test cascade operations
- Monitor query performance
