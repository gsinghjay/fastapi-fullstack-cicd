# FastAPI Full Stack Application with CI/CD Template

A modern FastAPI template built with best practices, async SQL support, and comprehensive testing.

## 🚀 Features

- FastAPI framework with async support
- Poetry for dependency management
- SQLAlchemy with async support
- Alembic for database migrations
- Comprehensive testing setup with pytest
- Code quality tools (Ruff, Black, MyPy)
- Semantic versioning and automated releases
- JWT Authentication
- CORS middleware configured
- Environment-based configuration
- Type hints and validation with Pydantic
- Exception handling
- Async database operations
- Dependency injection pattern
- Prometheus metrics
- Structured logging with structlog

## 📋 Prerequisites

- Python 3.11+
- Poetry for dependency management
- SQLite (default) or other supported databases

## 🛠️ Quick Start

1. Clone the repository:
```bash
git clone https://github.com/gsinghjay/fastapi-fullstack-cicd
cd fastapi-fullstack-cicd
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file in the root directory:
```env
APP_NAME="FastAPI App"
DEBUG=False
API_V1_STR="/api/v1"
DATABASE_URL="sqlite+aiosqlite:///./app.db"
SECRET_KEY="your-secret-key-here"  # Change this!
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

4. Run database migrations:
```bash
poetry run alembic upgrade head
```

5. Start the development server:
```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📦 Project Structure

```
fastapi-app/
├── app/
│   ├── __init__.py          # Package initializer with version
│   ├── main.py              # FastAPI application creation and configuration
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── security.py      # Security utilities (JWT, passwords)
│   │   └── exceptions.py    # Global exception handlers
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependency injection
│   │   └── v1/              # API version 1
│   │       ├── __init__.py
│   │       ├── router.py    # Main API router
│   │       └── endpoints/   # API endpoints by resource
│   │           ├── __init__.py
│   │           ├── health.py
│   │           └── users.py
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/              # Pydantic models
│   │   ├── __init__.py
│   │   └── user.py
│   └── crud/                 # Database operations
│       ├── __init__.py
│       └── user.py
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Test configuration and fixtures
│   └── api/
│       └── v1/
│           ├── test_health.py
│           └── test_users.py
├── alembic/                  # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── .github/                  # GitHub specific configuration
│   └── workflows/            # GitHub Actions workflows
│       └── release.yml       # Automated release workflow
├── alembic.ini               # Alembic configuration
├── .env                      # Environment variables
├── .gitignore                # Git ignore rules
├── pyproject.toml            # Project dependencies and configuration
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
└── README.md                 # Project documentation
```

## 🔄 Semantic Release

This project uses Python Semantic Release for versioning. Commit messages must follow the Angular Convention:

```
<type>(scope): <description>

[optional body]

[optional footer(s)]
```

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS protection
- Environment-based configuration
- Security headers middleware
- SQL injection protection
- Input validation with Pydantic

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🤝 Contributing

Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Development setup
- Coding standards
- Testing guidelines
- Pre-commit hooks
- CI/CD pipeline
- Pull request process

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
