import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.unit
@pytest.mark.anyio
async def test_health_check(async_client: AsyncClient) -> None:
    """Test the health check endpoint."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


@pytest.mark.unit
@pytest.mark.anyio
async def test_health_check_metrics(async_client: AsyncClient) -> None:
    """Test the health check metrics endpoint."""
    response = await async_client.get("/api/v1/health/metrics")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "operational"


@pytest.mark.unit
@pytest.mark.anyio
async def test_health_check_readiness(async_client: AsyncClient) -> None:
    """Test the health check readiness endpoint."""
    response = await async_client.get("/api/v1/health/readiness")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"


@pytest.mark.integration
@pytest.mark.anyio
async def test_db_connection(db_session: AsyncSession) -> None:
    """Test database connection."""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.integration
@pytest.mark.anyio
async def test_health_check_unhealthy(async_client: AsyncClient) -> None:
    """Test health check when database is unhealthy."""
    # TODO: Mock database to be down
    # For now, we'll just test the success case
    response = await async_client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
