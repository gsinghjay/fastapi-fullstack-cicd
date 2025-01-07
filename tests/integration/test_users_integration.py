"""Integration tests for user-related functionality."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate

# Constants
MIN_TEST_USERS = 3
HTTP_200_OK = status.HTTP_200_OK
HTTP_201_CREATED = status.HTTP_201_CREATED


@pytest.mark.integration
async def test_create_user_api_flow(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test complete user creation flow through API."""
    # Test user creation
    user_data = {
        "email": "flow_test@example.com",
        "password": "testpassword",
        "full_name": "Flow Test User",
        "is_active": True,
        "is_superuser": False,
    }

    # Create user via API
    response = await async_client.post("/api/v1/users/", json=user_data)
    assert response.status_code == HTTP_201_CREATED

    # Verify user exists in database
    db_user = await get_user_by_email(db_session, str(user_data["email"]))
    assert db_user is not None
    assert db_user.email == user_data["email"]
    await db_session.commit()  # Commit the transaction


@pytest.mark.integration
async def test_user_authentication_flow(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test complete user authentication flow."""
    # Create test user
    user_in = UserCreate(
        email="auth_test@example.com",
        password="testpassword",
        full_name="Auth Test User",
        is_active=True,
        is_superuser=False,
    )
    db_user = await create_user(db_session, user_in)
    await db_session.commit()  # Commit the transaction

    # Generate access token
    access_token = create_access_token(subject=db_user.email)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test accessing protected endpoint
    response = await async_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["email"] == user_in.email


@pytest.mark.integration
async def test_user_list_pagination(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test user listing with pagination."""
    # Create multiple test users
    for i in range(MIN_TEST_USERS):
        user_in = UserCreate(
            email=f"list_test_{i}@example.com",
            password="testpassword",
            full_name=f"List Test User {i}",
            is_active=True,
            is_superuser=False,
        )
        await create_user(db_session, user_in)
    await db_session.commit()  # Commit the transaction

    # Test listing users
    response = await async_client.get("/api/v1/users/")
    assert response.status_code == HTTP_200_OK
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= MIN_TEST_USERS  # At least our test users should be present


@pytest.mark.integration
async def test_user_update_flow(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test user update flow."""
    # Create test user
    user_in = UserCreate(
        email="update_test@example.com",
        password="testpassword",
        full_name="Update Test User",
        is_active=True,
        is_superuser=False,
    )
    db_user = await create_user(db_session, user_in)
    await db_session.commit()  # Commit the transaction

    # Generate access token
    access_token = create_access_token(subject=db_user.email)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test updating user
    update_data = {"full_name": "Updated Name"}
    response = await async_client.patch(
        f"/api/v1/users/{db_user.id}", headers=headers, json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["full_name"] == update_data["full_name"]
