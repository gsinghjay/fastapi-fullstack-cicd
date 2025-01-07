"""Unit tests for user-related functionality."""
import pytest
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.users import create_user as create_user_handler
from app.api.v1.endpoints.users import login
from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate

# Constants
HTTP_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST
HTTP_401_UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
async def test_create_user_handler_validation(db_session: AsyncSession) -> None:
    """Test user creation input validation."""
    # Test with invalid email
    user_data = UserCreate(
        email="invalid-email",
        password="testpassword",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    with pytest.raises(ValueError):
        await create_user_handler(user_data, db_session)

    # Test with short password
    user_data = UserCreate(
        email="test@example.com",
        password="short",  # too short
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    with pytest.raises(ValueError):
        await create_user_handler(user_data, db_session)


@pytest.mark.unit
async def test_create_user_duplicate_email(db_session: AsyncSession) -> None:
    """Test creating user with duplicate email."""
    user_data = UserCreate(
        email="duplicate@example.com",
        password="testpassword",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )

    # Create first user
    await create_user(db_session, user_data)

    # Attempt to create second user with same email
    with pytest.raises(HTTPException) as exc_info:
        await create_user_handler(user_data, db_session)

    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST
    assert "Email already registered" in str(exc_info.value.detail)


@pytest.mark.unit
async def test_get_user_by_email_not_found(db_session: AsyncSession) -> None:
    """Test getting non-existent user by email."""
    user = await get_user_by_email(db_session, "nonexistent@example.com")
    assert user is None


@pytest.mark.unit
async def test_user_password_hashing(db_session: AsyncSession) -> None:
    """Test that user passwords are properly hashed."""
    user_data = UserCreate(
        email="hash_test@example.com",
        password="testpassword",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )

    db_user = await create_user(db_session, user_data)
    assert db_user.hashed_password != user_data.password
    assert len(db_user.hashed_password) > 0


@pytest.mark.unit
async def test_login_success(db_session: AsyncSession) -> None:
    """Test successful login."""
    # Create test user
    user_data = UserCreate(
        email="login_test@example.com",
        password="testpassword",
        full_name="Login Test User",
        is_active=True,
        is_superuser=False,
    )
    await create_user(db_session, user_data)

    # Test login
    form_data = OAuth2PasswordRequestForm(
        username=user_data.email,
        password=user_data.password,
        scope="",
        grant_type="password",
    )
    token = await login(form_data, db_session)
    assert token.access_token
    assert token.token_type == "bearer"


@pytest.mark.unit
async def test_login_invalid_credentials(db_session: AsyncSession) -> None:
    """Test login with invalid credentials."""
    # Create test user
    user_data = UserCreate(
        email="invalid_login@example.com",
        password="testpassword",
        full_name="Invalid Login User",
        is_active=True,
        is_superuser=False,
    )
    await create_user(db_session, user_data)

    # Test login with wrong password
    form_data = OAuth2PasswordRequestForm(
        username=user_data.email,
        password="wrongpassword",
        scope="",
        grant_type="password",
    )
    with pytest.raises(HTTPException) as exc_info:
        await login(form_data, db_session)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in str(exc_info.value.detail)

    # Test login with wrong email
    form_data = OAuth2PasswordRequestForm(
        username="wrong@example.com",
        password=user_data.password,
        scope="",
        grant_type="password",
    )
    with pytest.raises(HTTPException) as exc_info:
        await login(form_data, db_session)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in str(exc_info.value.detail)


@pytest.mark.unit
async def test_login_inactive_user(db_session: AsyncSession) -> None:
    """Test login with inactive user."""
    # Create inactive test user
    user_data = UserCreate(
        email="inactive@example.com",
        password="testpassword",
        full_name="Inactive User",
        is_active=False,
        is_superuser=False,
    )
    await create_user(db_session, user_data)

    # Test login
    form_data = OAuth2PasswordRequestForm(
        username=user_data.email,
        password=user_data.password,
        scope="",
        grant_type="password",
    )
    with pytest.raises(HTTPException) as exc_info:
        await login(form_data, db_session)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert "User is inactive" in str(exc_info.value.detail)
