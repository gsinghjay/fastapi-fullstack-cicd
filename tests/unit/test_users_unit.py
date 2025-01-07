"""Unit tests for user-related functionality."""
import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.users import create_user as create_user_handler
from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate

# Constants
HTTP_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST


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
