from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.

    Yields:
        AsyncSession: The database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Create reusable dependencies
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(
    token: CurrentUser,
    db: DBSession,
) -> dict:
    """
    Dependency for getting current authenticated user.

    Args:
        token: The JWT token from the request.
        db: The database session.

    Returns:
        dict: The current user's data.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    return payload
