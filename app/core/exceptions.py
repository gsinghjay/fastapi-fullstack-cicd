from typing import Any, TypeVar

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

T = TypeVar("T")


class AppError(Exception):
    """Base exception class for application errors."""

    def __init__(
        self,
        status_code: int,
        detail: str | dict[str, Any],
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


def configure_exceptions(app: FastAPI) -> None:
    """Configure exception handlers for the FastAPI application."""

    @app.exception_handler(AppError)  # type: ignore[misc]
    async def app_exception_handler(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        """Handle AppError exceptions."""
        headers = exc.headers or {}
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )

    @app.exception_handler(StarletteHTTPException)  # type: ignore[misc]
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)  # type: ignore[misc]
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unhandled exceptions."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
