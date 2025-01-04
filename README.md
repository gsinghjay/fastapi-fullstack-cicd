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
- pyenv (recommended for Python version management)
- SQLite (default) or other supported databases

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/gsinghjay/fastapi-fullstack-cicd
cd fastapi-fullstack-cicd
```

2. Install pyenv and Python 3.11:
```bash
# Install pyenv prerequisites
sudo apt update && sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Install pyenv
curl https://pyenv.run | bash

# Add to your bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.11
pyenv install 3.11
pyenv local 3.11
```

3. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

4. Add Poetry to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

5. Install project dependencies:
```bash
poetry install
```

6. Create a `.env` file in the root directory:
```env
APP_NAME="FastAPI App"
DEBUG=False
API_V1_STR="/api/v1"
DATABASE_URL="sqlite+aiosqlite:///./app.db"
SECRET_KEY="your-secret-key-here"  # Change this!
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

## 🚀 Running the Application

1. Activate the virtual environment:
```bash
poetry shell
```

2. Run database migrations:
```bash
alembic upgrade head
```

3. Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`

## 🧪 Testing

Run tests with pytest:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=app tests/
```

## 🔍 Code Quality

This project uses several tools to ensure code quality. All tools can be run using Poetry scripts:

1. Format and lint code:
```bash
poetry run ruff check .  # Lint
poetry run ruff format .  # Format
```

2. Type checking:
```bash
poetry run mypy .
```

3. Security checks:
```bash
poetry run bandit -r app/
poetry run safety check
```

4. Run all quality checks using pre-commit:
```bash
poetry run pre-commit run --all-files
```

## 📦 Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. The hooks run automatically on each commit, but you can also run them manually:

```bash
# Install the pre-commit hooks
poetry run pre-commit install

# Run all hooks against all files
poetry run pre-commit run --all-files
```

The following checks are performed:
- **Code Quality**
  - Trailing whitespace removal
  - File ending normalization
  - YAML/TOML syntax validation
  - Large file checks (>1MB)
  - Debug statement checks
  - Private key detection
  - Merge conflict detection
  - Case conflict detection
  - Line ending normalization
- **Code Formatting & Linting**
  - Ruff for Python linting and formatting
- **Type Checking**
  - MyPy for static type checking
- **Security**
  - Bandit for security vulnerability scanning
- **Commit Messages**
  - Semantic Release for enforcing conventional commit format
- **Dependencies**
  - Poetry for checking dependency consistency

If any check fails, the commit will be blocked until the issues are fixed. You can fix most issues automatically by running:
```bash
poetry run pre-commit run --all-files
```

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

Types include:
- feat: New feature (minor version)
- fix: Bug fix (patch version)
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- perf: Performance improvements
- test: Adding or modifying tests
- build: Build system changes
- ci: CI configuration changes
- chore: General maintenance
- revert: Revert previous changes

Breaking changes must be indicated by "BREAKING CHANGE:" in the commit footer or by appending ! after the type/scope.

## 🔒 Security

- All passwords are hashed using bcrypt
- JWT tokens for authentication
- CORS protection
- Environment variables for sensitive data
- Security headers middleware
- Rate limiting (TODO)
- SQL injection protection through SQLAlchemy
- Input validation through Pydantic

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JWT Documentation](https://python-jose.readthedocs.io/)
