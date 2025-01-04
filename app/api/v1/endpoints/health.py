from collections.abc import Mapping

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.deps import DBSession

router = APIRouter()


@router.get(
    "",
    response_model=dict[str, str],
    responses={
        200: {
            "description": "Health check passed",
            "content": {
                "application/json": {
                    "example": {"status": "healthy", "database": "connected"}
                }
            },
        },
        503: {
            "description": "Health check failed",
            "content": {
                "application/json": {
                    "example": {"status": "unhealthy", "database": "disconnected"}
                }
            },
        },
    },
    response_description="Health check status",
    summary="Health Check",
    description="Health check endpoint that verifies database connection",
)
async def health_check(
    response: Response,
    db: DBSession,
) -> Mapping[str, str]:
    """
    Health check endpoint that verifies database connection.

    Args:
        response: FastAPI response object.
        db: The database session.

    Returns:
        A dictionary containing the health status of the application and database.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "database": "disconnected"}


@router.get(
    "/metrics",
    response_model=dict[str, str],
    responses={
        200: {
            "description": "Application metrics",
            "content": {"application/json": {"example": {"status": "operational"}}},
        },
    },
    response_description="Application metrics",
    summary="Application Metrics",
    description="Get application metrics and status",
)
async def health_check_metrics() -> dict[str, str]:
    """
    Get application metrics.

    Returns:
        A dictionary containing application metrics.
    """
    return {"status": "operational"}


@router.get(
    "/readiness",
    response_model=dict[str, str],
    responses={
        200: {
            "description": "Application is ready",
            "content": {"application/json": {"example": {"status": "ready"}}},
        },
    },
    response_description="Application readiness status",
    summary="Readiness Check",
    description="Check if the application is ready to handle requests",
)
async def health_check_readiness() -> dict[str, str]:
    """
    Check application readiness.

    Returns:
        A dictionary containing the readiness status.
    """
    return {"status": "ready"}
