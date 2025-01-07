from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


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
    """
    user_data = user_in.model_dump(exclude={"password"})
    db_user = User(
        **user_data,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    """
    Update user.

    Args:
        db: The database session.
        db_user: The user to update.
        user_in: The user data to update with.

    Returns:
        The updated user.
    """
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
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
