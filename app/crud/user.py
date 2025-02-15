from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

__all__ = [
    "get_users",
    "get_user_by_email",
    "create_user",
    "update_user",
    "get_user_by_id",
    "get_active_superuser_count",
]


async def get_users(db: AsyncSession) -> list[User]:
    """
    Get all users.

    Args:
        db: The database session.

    Returns:
        List of all users.
    """
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Get a user by email.

    Args:
        db: The database session.
        email: The email to look up.

    Returns:
        The user if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Create new user.

    Args:
        db: The database session.
        user_in: The user data to create.

    Returns:
        The created user.

    Raises:
        HTTPException: If the email is already registered.
    """
    user_data = user_in.model_dump(exclude={"password"})
    db_user = User(
        **user_data,
        hashed_password=get_password_hash(user_in.password),
    )

    try:
        async with db.begin_nested():  # Create a savepoint
            db.add(db_user)
            await db.flush()  # Just flush to get the ID
            await db.refresh(db_user)
            return db_user
    except IntegrityError as e:
        if "ix_users_email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            ) from e
        raise  # Re-raise other integrity errors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        ) from e


async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    """
    Update user.

    Args:
        db: The database session.
        db_user: The user to update.
        user_in: The user data to update with.

    Returns:
        The updated user.

    Raises:
        HTTPException: If the update fails or validation fails.
    """
    try:
        update_data = user_in.model_dump(exclude_unset=True)

        # Handle password update
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        # Validate email uniqueness if it's being updated
        if "email" in update_data and update_data["email"] != db_user.email:
            existing_user = await get_user_by_email(db, update_data["email"])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

        # Update user fields
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        return db_user
    except Exception as e:
        import logging

        logging.error("Error in update_user: %s", str(e), exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user: " + str(e),
        ) from e


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """
    Get a user by ID.

    Args:
        db: The database session.
        user_id: The user ID to look up.

    Returns:
        The user if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_active_superuser_count(db: AsyncSession) -> int:
    """
    Get the count of active superusers.

    Args:
        db: The database session.

    Returns:
        The number of active superusers.
    """
    result = await db.execute(
        select(User).where(User.is_superuser == True, User.is_active == True)  # noqa: E712
    )
    return len(list(result.scalars().all()))
