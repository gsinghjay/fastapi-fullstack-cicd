# CHANGELOG


## v1.0.0 (2025-01-07)

### Features

- **auth**: Implement user login endpoint
  ([`e8d6c8a`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/e8d6c8a6fe65dc853988c954627391d8d4411dd2))

- Add login endpoint with OAuth2 password flow - Add token response schema - Add comprehensive login
  unit tests - Handle invalid credentials and inactive users - Restore UserUpdate schema

### Testing

- **users**: Reorganize test structure with unit/integration/regression
  ([`cfe044b`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/cfe044bcde8d298aab0af2ae30580bae70a1067b))

- Split tests into unit, integration, and regression categories - Add pytest markers for test types
  - Improve test fixtures and isolation - Add comprehensive test cases for user functionality -
  Configure async test support in pytest - Fix linting and typing issues

BREAKING CHANGE: Test file structure has been reorganized. Old test_users.py has been split into
  separate files under tests/{unit,integration,regression} directories.

### BREAKING CHANGES

- **users**: Test file structure has been reorganized. Old test_users.py has been split into
  separate files under tests/{unit,integration,regression} directories.


## v0.2.0 (2025-01-04)

### Code Style

- **crud**: Update type annotations to use modern syntax
  ([`1eebf9a`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/1eebf9a70444ef79b3d9b42ceb48ed00eede80e4))

### Documentation

- **contributing**: Enhance testing and type checking guidelines
  ([`a0684c1`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/a0684c1f012ec9d87afeaa0c7b35d70f6d383a27))

Added sections on type checking configuration and pre-commit setup. Enhanced documentation for async
  testing best practices with examples of fixtures and type annotations.

- **contributing**: Update testing guidelines and best practices
  ([`9412a52`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/9412a520db3d97583df5010ddd6fc297d657f2ff))

- **qa**: Add comprehensive quality assurance documentation
  ([`a7dc50c`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/a7dc50c20fc6292ba66c5e24af3a87e76453ed21))

- **readme**: Simplify and improve user focus
  ([`1c6176e`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/1c6176e660c82abdad522820c81cc3562de67ece))

Streamlined README.md by removing duplicate content from CONTRIBUTING.md. Improved quick start guide
  and focused on essential user information.

### Features

- **api**: Add health check endpoints with database verification
  ([`e7e52a7`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/e7e52a7d75abefe9556fbec1be71395e689fa74c))

- **db**: Add SQLAlchemy base class with common model functionality
  ([`ee41253`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/ee412532c7a95eccfa144987c556bcd8220cfa9c))

- **db**: Implement async session management with proper typing
  ([`3b7f14c`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/3b7f14c3d9641337385386fa1109d0337239f48f))

- **infra**: Add Docker and PostgreSQL test infrastructure
  ([`24ba312`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/24ba3128b92e821f99037c02587a5c6fbdac1409))

- Add Docker test configuration - Configure test environment variables - Add PostgreSQL container
  setup - Update project dependencies

- **tests**: Implement pytest fixtures for database and Docker testing
  ([`2f13465`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/2f13465cf87ef754922cde7abb1c3416c3628856))

### Refactoring

- **api**: Improve user endpoints with better error handling
  ([`acf5da8`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/acf5da8adb7d1e9795c73f39e2eee3c1ca588845))

- **config**: Update configuration management for test environment
  ([`1a540b8`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/1a540b8f8639b782d26c6b1362d708d7c4695797))

- **db**: Reorganize database initialization and configuration
  ([`a1479e0`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/a1479e0c3d723d17710103f5c7203b240561ae70))

- **deps**: Update dependency injection with proper async handling
  ([`eff48e3`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/eff48e37f5527c06000207e18fdc801e224f14c2))

- **models**: Enhance user model with better type definitions
  ([`b767086`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/b767086a45a5d108341f909cadf03ec2ae25c6ad))

- **schemas**: Update user schemas with improved validation
  ([`d72ba08`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/d72ba08216af9ffeab3de559b3f6be7a04835613))

- **test**: Enhance testing infrastructure and type safety
  ([`683b175`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/683b175b25987b3a8457b6257e78b7cf56859142))

- Added comprehensive async testing setup with proper fixtures and type annotations. - Updated
  testing documentation with FastAPI best practices. - Improved type checking with stricter mypy
  configuration and proper type stubs. - Configured pre-commit to use project's mypy settings.

### Testing

- **api**: Add health check endpoint tests
  ([`7795ada`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/7795ada1841d8b43c9c1d3969576d14dcdc10851))


## v0.1.0 (2025-01-04)

### Chores

- **git**: Add git configuration files
  ([`5618272`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/56182720d39b567f54a91e10928bbec291d889cc))

- Add .gitignore for Python projects - Configure git attributes - Set up repository templates

- **tools**: Add development tools and configurations
  ([`9cd266d`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/9cd266d7b68c23c7a62696be4cd4853874029684))

- Configure pre-commit hooks - Add linting and formatting tools - Set up mypy for type checking -
  Add commitlint configuration

### Continuous Integration

- **workflow**: Add GitHub Actions workflow
  ([`41f4406`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/41f440621148cc0594ab76dfd3414bacc71ad860))

- Configure semantic release workflow - Set up automated testing and deployment - Add release
  configuration

### Documentation

- **project**: Add project documentation
  ([`0cd93a0`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/0cd93a0584601c8d012dd26714aa5832077c5408))

- Add comprehensive README - Create CONTRIBUTING guidelines - Add code documentation and docstrings
  - Include license information

### Features

- **api**: Add core API endpoints and routing
  ([`8ccbeb0`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/8ccbeb09d0a36c77c651eda28abc6286853c4bf8))

- Implement health check endpoint - Add user management endpoints - Set up API router with
  versioning - Configure dependency injection system

- **config**: Add project configuration and environment setup
  ([`ec5faa8`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/ec5faa8a6d496fcce67f20d58321659aeaecf897))

- Add core configuration management - Set up environment variables handling - Configure logging and
  exception handling - Add security utilities for JWT and password hashing

- **database**: Implement database configuration and models
  ([`2a5af41`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/2a5af41831bb9238db023e2ec1ccf264fa41cd53))

- Add SQLAlchemy async database setup - Create User model and schemas - Configure Alembic for
  migrations - Implement CRUD operations

- **project**: Initialize FastAPI project structure
  ([`90e2afb`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/90e2afb56cc4a3a526b433c87492d157a463dd62))

- Set up basic project directory structure - Add main FastAPI application entry point - Configure
  project metadata and dependencies

### Testing

- **setup**: Configure testing infrastructure
  ([`44357e7`](https://github.com/gsinghjay/fastapi-fullstack-cicd/commit/44357e796c9966fdfaaefaeea4a7026f9a01268f))

- Add pytest configuration and fixtures - Set up test database handling - Configure test client
