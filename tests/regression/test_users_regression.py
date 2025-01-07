"""Regression tests for user-related functionality."""
import asyncio

import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.crud.user import create_user, get_user_by_email
from app.schemas.user import UserCreate

# Constants
MAX_CONCURRENT_REQUESTS = 3
HTTP_401_UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
HTTP_200_OK = status.HTTP_200_OK
HTTP_201_CREATED = status.HTTP_201_CREATED


@pytest.mark.regression
async def test_concurrent_user_creation(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test concurrent user creation with same email."""
    user_data = {
        "email": "concurrent@example.com",
        "password": "testpassword",
        "full_name": "Concurrent Test User",
        "is_active": True,
        "is_superuser": False,
    }

    # Simulate concurrent requests
    responses = await asyncio.gather(
        *[
            async_client.post("/api/v1/users/", json=user_data)
            for _ in range(MAX_CONCURRENT_REQUESTS)
        ],
        return_exceptions=True,
    )

    # Only one request should succeed
    success_count = sum(
        1
        for r in responses
        if isinstance(r, Response) and r.status_code == HTTP_201_CREATED
    )
    assert success_count == 1

    # Verify only one user exists in database
    db_user = await get_user_by_email(db_session, str(user_data["email"]))
    assert db_user is not None
    assert db_user.email == user_data["email"]


@pytest.mark.regression
async def test_user_session_invalidation(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test user session handling after password change."""
    # Create test user
    user_in = UserCreate(
        email="session_test@example.com",
        password="oldpassword",
        full_name="Session Test User",
        is_active=True,
        is_superuser=False,
    )
    db_user = await create_user(db_session, user_in)

    # Generate initial access token
    old_token = create_access_token(subject=db_user.email)
    headers = {"Authorization": f"Bearer {old_token}"}

    # Change password
    new_password = "newpassword"
    response = await async_client.post(
        "/api/v1/users/me/change-password",
        headers=headers,
        json={"current_password": "oldpassword", "new_password": new_password},
    )
    assert response.status_code == status.HTTP_200_OK

    # Old token should be invalid
    response = await async_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.regression
async def test_user_deactivation_flow(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test complete user deactivation flow."""
    # Create test user
    user_in = UserCreate(
        email="deactivate_test@example.com",
        password="testpassword",
        full_name="Deactivate Test User",
        is_active=True,
        is_superuser=False,
    )
    db_user = await create_user(db_session, user_in)

    # Generate access token
    access_token = create_access_token(subject=db_user.email)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Deactivate user
    response = await async_client.post(
        f"/api/v1/users/{db_user.id}/deactivate",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify user can't login
    response = await async_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.regression
async def test_user_data_consistency(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test user data consistency across multiple operations."""
    # Create initial user
    user_in = UserCreate(
        email="consistency_test@example.com",
        password="testpassword",
        full_name="Consistency Test User",
        is_active=True,
        is_superuser=False,
    )
    db_user = await create_user(db_session, user_in)
    access_token = create_access_token(subject=db_user.email)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Perform multiple updates
    updates = [
        {"full_name": "Updated Name 1"},
        {"full_name": "Updated Name 2"},
        {"is_active": False},
        {"is_active": True},
        {"full_name": "Final Name"},
    ]

    for update in updates:
        response = await async_client.patch(
            f"/api/v1/users/{db_user.id}",
            headers=headers,
            json=update,
        )
        assert response.status_code == status.HTTP_200_OK

    # Verify final state
    response = await async_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    final_user = response.json()
    assert final_user["full_name"] == "Final Name"
    assert final_user["is_active"] is True
