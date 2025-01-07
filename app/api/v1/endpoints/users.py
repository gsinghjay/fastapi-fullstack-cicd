from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.api.deps import DBSession, get_current_user, invalidate_user_sessions
from app.core.security import create_access_token, verify_password
from app.crud.user import (
    create_user,
    get_active_superuser_count,
    get_user_by_email,
    get_user_by_id,
    get_users,
    update_user,
)
from app.models.user import User as UserModel
from app.schemas.user import Token, User, UserCreate, UserUpdate


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str
    new_password: str


router = APIRouter()


@router.get("/", response_model=list[User])
async def list_users_endpoint(
    db: DBSession,
) -> list[User]:
    """
    List all users endpoint handler.

    Args:
        db: The database session.

    Returns:
        List of users.
    """
    users = await get_users(db)
    return [User.model_validate(user) for user in users]


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_in: UserCreate,
    db: DBSession,
) -> User:
    """
    Create new user endpoint handler.

    Args:
        user_in: The user data to create.
        db: The database session.

    Returns:
        The created user.

    Raises:
        HTTPException: If the email is already registered.
    """
    user = await get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    db_user = await create_user(db, user_in)
    await db.commit()  # Commit the transaction
    return User.model_validate(db_user)


@router.get("/me", response_model=User)
async def read_user_me_endpoint(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> User:
    """
    Get current user endpoint handler.

    Args:
        current_user: The current user.

    Returns:
        The current user's details.
    """
    return User.model_validate(current_user)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        form_data: The login form data.
        db: The database session.

    Returns:
        The access token.

    Raises:
        HTTPException: If authentication fails.
    """
    user = await get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return Token(
        access_token=create_access_token(subject=user.email),
        token_type="bearer",
    )


@router.patch("/{user_id}", response_model=User)
async def update_user_endpoint(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: DBSession,
) -> User:
    """
    Update user endpoint handler.

    Args:
        user_id: The ID of the user to update.
        user_update: The user data to update.
        current_user: The current authenticated user.
        db: The database session.

    Returns:
        The updated user.

    Raises:
        HTTPException: If the user is not found or if the current user lacks permission.
    """
    try:
        async with db.begin():
            # Check if user exists and get fresh data
            db_user = await get_user_by_id(db, user_id)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            # Check permissions (only superuser or the user themselves can update)
            if not current_user.is_superuser and current_user.id != db_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )

            # Prevent removing superuser status from the last superuser
            if db_user.is_superuser and user_update.is_superuser is False:
                # Count active superusers
                active_superusers = await get_active_superuser_count(db)
                if active_superusers <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot remove superuser status from the last superuser",
                    )

            # Update user
            updated_user = await update_user(db, db_user, user_update)
            await db.refresh(updated_user)  # Ensure we have the latest data
            return User.model_validate(updated_user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        ) from e


@router.post("/{user_id}/deactivate", response_model=User)
async def deactivate_user_endpoint(
    user_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: DBSession,
) -> User:
    """
    Deactivate user endpoint handler.

    Args:
        user_id: The ID of the user to deactivate.
        current_user: The current authenticated user.
        db: The database session.

    Returns:
        The deactivated user.

    Raises:
        HTTPException: If the user is not found or if the current user lacks permission.
    """
    try:
        async with db.begin():
            # Only superusers can deactivate users
            if not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )

            # Check if user exists and get fresh data
            db_user = await get_user_by_id(db, user_id)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            # Prevent deactivating the last superuser
            if db_user.is_superuser:
                # Count active superusers
                active_superusers = await get_active_superuser_count(db)
                if active_superusers <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot deactivate the last superuser",
                    )

            # Deactivate user
            user_update = UserUpdate(is_active=False)
            updated_user = await update_user(db, db_user, user_update)
            await db.refresh(updated_user)  # Ensure we have the latest data

            # Invalidate all existing sessions for this user
            invalidate_user_sessions(str(updated_user.id))

            return User.model_validate(updated_user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user",
        ) from e


@router.post("/{user_id}/change-password", response_model=User)
async def change_password_endpoint(
    user_id: UUID,
    password_change: PasswordChange,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: DBSession,
) -> User:
    """
    Change user password endpoint handler.

    Args:
        user_id: The ID of the user to update.
        password_change: The password change data.
        current_user: The current authenticated user.
        db: The database session.

    Returns:
        The updated user.

    Raises:
        HTTPException: If the user is not found, current password is incorrect,
                      or if the current user lacks permission.
    """
    try:
        async with db.begin():
            # Check if user exists and get fresh data
            db_user = await get_user_by_id(db, user_id)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            # Check permissions
            # Only superuser or the user themselves can change password
            if not current_user.is_superuser and current_user.id != db_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )

            # Verify current password
            if not verify_password(
                password_change.current_password,
                db_user.hashed_password,
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect password",
                )

            # Update password
            user_update = UserUpdate(password=password_change.new_password)
            updated_user = await update_user(db, db_user, user_update)
            await db.refresh(updated_user)  # Ensure we have the latest data

            # Invalidate all existing sessions for this user
            invalidate_user_sessions(str(updated_user.id))

            return User.model_validate(updated_user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        ) from e


@router.get("/{user_id}", response_model=User)
async def get_user_endpoint(
    user_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: DBSession,
) -> User:
    """
    Get user by ID endpoint handler.

    Args:
        user_id: The ID of the user to retrieve.
        current_user: The current authenticated user.
        db: The database session.

    Returns:
        The user details.

    Raises:
        HTTPException: If the user is not found or if the current user lacks permission.
    """
    try:
        async with db.begin():
            # Check if user exists and get fresh data
            db_user = await get_user_by_id(db, user_id)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            # Check permissions (only superuser or the user themselves can view details)
            if not current_user.is_superuser and current_user.id != db_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )

            return User.model_validate(db_user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        ) from e


@router.post("/me/change-password", response_model=User)
async def change_password_me_endpoint(
    password_change: PasswordChange,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: DBSession,
) -> User:
    """
    Change current user's password endpoint handler.

    Args:
        password_change: The password change data.
        current_user: The current authenticated user.
        db: The database session.

    Returns:
        The updated user.

    Raises:
        HTTPException: If the current password is incorrect.
    """
    return await change_password_endpoint(
        user_id=current_user.id,
        password_change=password_change,
        current_user=current_user,
        db=db,
    )
