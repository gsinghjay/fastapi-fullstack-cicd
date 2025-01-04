import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.crud.user import create_user
from app.schemas.user import UserCreate


@pytest.mark.integration
@pytest.mark.anyio
async def test_create_user(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test user creation."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
    }
    response = await async_client.post("/api/v1/users/", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data


@pytest.mark.integration
@pytest.mark.anyio
async def test_get_user(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test getting user details."""
    # Create a user first
    user_in = UserCreate(
        email="get@example.com",
        password="testpassword",
        full_name="Get User",
        is_active=True,
        is_superuser=False,
    )

    # Create user directly through CRUD
    db_user = await create_user(db_session, user_in)
    await db_session.commit()  # Commit to make the user visible to other sessions

    # Create access token for authentication
    access_token = create_access_token(subject=db_user.email)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test getting user through API
    response = await async_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_in.email
    assert data["full_name"] == user_in.full_name


@pytest.mark.integration
@pytest.mark.anyio
async def test_read_users(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test reading users list."""
    # Create a test user first
    user_in = UserCreate(
        email="list@example.com",
        password="testpassword",
        full_name="List User",
        is_active=True,
        is_superuser=False,
    )
    await create_user(db_session, user_in)
    await db_session.commit()  # Commit to make the user visible to other sessions

    response = await async_client.get("/api/v1/users/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
