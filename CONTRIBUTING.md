# Contributing to FastAPI Full-Stack CI/CD Template

Thank you for your interest in contributing to our FastAPI Full-Stack CI/CD template! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Environment](#development-environment)
  - [Installation](#installation)
- [Development Workflow](#development-workflow)
  - [Branching Strategy](#branching-strategy)
  - [Commit Messages](#commit-messages)
  - [Pull Requests](#pull-requests)
- [Coding Standards](#coding-standards)
  - [FastAPI Best Practices](#fastapi-best-practices)
  - [Python Style Guide](#python-style-guide)
  - [Type Hints](#type-hints)
  - [Documentation](#documentation)
  - [Testing](#testing)
- [Pre-commit Hooks](#pre-commit-hooks)
- [CI/CD Pipeline](#cicd-pipeline)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to adhere to our Code of Conduct.

## Getting Started

### Development Environment

1. Python 3.11 or higher
2. Poetry for dependency management
3. Git for version control
4. A suitable IDE (we recommend VS Code with Python extensions)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-fullstack-cicd.git
   cd fastapi-fullstack-cicd
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- Feature branches: `feature/your-feature-name`
- Bug fix branches: `fix/bug-description`
- Release branches: `release/vX.Y.Z`

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Example:
```
feat(auth): add JWT authentication system

- Implement JWT token generation
- Add token validation middleware
- Update user routes with authentication

Closes #123
```

### Pull Requests

1. Create a new branch from `develop`
2. Make your changes
3. Run tests and ensure all checks pass
4. Submit a PR to `develop`
5. Request review from maintainers
6. Address review comments
7. Squash and merge when approved

## Coding Standards

### FastAPI Best Practices

Follow the official [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) guidelines:

1. **Path Operations**:
   - Use semantic HTTP methods (GET, POST, PUT, DELETE)
   - Group related endpoints using APIRouter
   - Use path parameters for required values
   - Use query parameters for optional values

2. **Request/Response Models**:
   - Always use Pydantic models for request/response validation
   - Create separate models for different purposes (e.g., UserCreate, UserUpdate, UserInDB)
   - Use Field for additional validation

3. **Dependencies**:
   - Use FastAPI's Dependency Injection system
   - Create reusable dependencies for common operations
   - Use yield dependencies for cleanup operations

4. **Security**:
   - Use OAuth2 with JWT tokens
   - Implement proper password hashing
   - Use HTTPBearer for token validation

5. **Error Handling**:
   - Use HTTPException for API errors
   - Create custom exception handlers when needed
   - Return appropriate status codes

6. **Database**:
   - Use async SQLAlchemy for database operations
   - Implement proper connection pooling
   - Use migrations for database changes

7. **Performance**:
   - Use async/await for I/O operations
   - Implement proper caching strategies
   - Use background tasks for long-running operations

### Python Style Guide

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [Ruff](https://beta.ruff.rs/docs/) for linting
- Maximum line length: 88 characters (Black default)

### Type Hints

- Use type hints for all function arguments and return values
- Follow [PEP 484](https://peps.python.org/pep-0484/) for type hints
- Use `mypy` for static type checking
- Prefer using the `|` operator over `Union` for type hints
- Use `Annotated` for dependency injection
- Example:
  ```python
  from typing import Annotated

  async def get_user(
      user_id: int,
      db: Annotated[AsyncSession, Depends(get_db)]
  ) -> User:
      ...
  ```

### Documentation

- Write docstrings for all public modules, functions, classes, and methods
- Follow [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings
- Include type information in docstrings
- Document exceptions that may be raised
- Example:
  ```python
  async def create_user(
      user_in: UserCreate,
      db: AsyncSession,
  ) -> User:
      """
      Create new user.

      Args:
          user_in: The user data to create.
          db: The database session.

      Returns:
          The created user.

      Raises:
          HTTPException: If the email is already registered.
      """
  ```

### Testing

- Write unit tests for all new code
- Use pytest for testing
- Maintain test coverage above 80%
- Write both sync and async tests as needed
- Use fixtures for common test setups
- Follow FastAPI's testing guidelines:

#### Synchronous Testing
```python
from fastapi.testclient import TestClient

def test_read_main(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

#### Asynchronous Testing
For async database operations or when you need to test async functionality:
```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.anyio
async def test_async_operation(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
```

#### Testing Best Practices
- Use `@pytest.mark.anyio` for async test functions
- Use `AsyncClient` with `ASGITransport` for async API testing
- Use async fixtures for database operations
- Properly handle test database setup and teardown
- Use dependency overrides for mocking dependencies
- Ensure proper event loop handling in async tests
- If using lifespan events, use `LifespanManager` from asgi-lifespan
- Create fixtures in `conftest.py` for reusable test components
- Use proper type annotations in test functions and fixtures

#### Test Database Handling
```python
@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    """Create all tables for testing and clean up after tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

#### Event Loop Handling
```python
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality. The following checks are run:

1. trim trailing whitespace
2. fix end of files
3. check yaml
4. check toml
5. check for large files
6. debug statements
7. detect private keys
8. check for merge conflicts
9. check for case conflicts
10. mixed line ending
11. ruff (linting)
12. ruff-format (formatting)
13. mypy (type checking)
14. bandit (security)
15. poetry check

To run checks manually:
```bash
poetry run pre-commit run --all-files
```

## CI/CD Pipeline

Our CI/CD pipeline includes:

1. Code Quality Checks:
   - Linting with Ruff
   - Type checking with mypy
   - Security scanning with Bandit
   - Code formatting with Black

2. Testing:
   - Unit tests
   - Integration tests
   - Coverage reporting

3. Deployment:
   - Automatic deployment to staging
   - Manual approval for production
   - Version tagging
   - Changelog generation
