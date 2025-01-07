from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.crud.user import get_user_by_email
from app.db.session import AsyncSessionLocal
from app.models.user import User

# Store of invalidated tokens with their expiry time
# In a real application, this would be in Redis or similar
INVALIDATED_TOKENS: dict[str, datetime] = {}


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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/login")

# Create reusable dependencies
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[str, Depends(oauth2_scheme)]


def invalidate_user_sessions(user_id: str) -> None:
    """
    Invalidate all sessions for a user.

    Args:
        user_id: The user ID whose sessions to invalidate.
    """
    # In a real application, this would be stored in Redis or similar
    # with proper expiry handling
    INVALIDATED_TOKENS[user_id] = datetime.utcnow()


async def get_current_user(
    token: CurrentUser,
    db: DBSession,
) -> User:
    """
    Dependency for getting current authenticated user.

    Args:
        token: The JWT token from the request.
        db: The database session.

    Returns:
        The current user.

    Raises:
        HTTPException: If the credentials are invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception

        # Get token creation time
        iat = payload.get("iat")
        if iat is None:
            raise credentials_exception
    except HTTPException as e:
        raise e
    except Exception as e:
        raise credentials_exception from e

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Check if user's sessions have been invalidated
    invalidation_time = INVALIDATED_TOKENS.get(str(user.id))
    if invalidation_time and datetime.fromtimestamp(iat, UTC) < invalidation_time:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
