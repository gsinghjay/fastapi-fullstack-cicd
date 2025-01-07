from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.api.deps import DBSession, get_current_user
from app.core.security import create_access_token, verify_password
from app.crud import user as user_crud
from app.models.user import User as UserModel
from app.schemas.user import Token, User, UserCreate, UserUpdate


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str
    new_password: str


router = APIRouter()


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
    return await list_users(db)


async def list_users(
    db: DBSession,
) -> list[User]:
    """
    List all users.

    Args:
        db: The database session.

    Returns:
        List of users.
    """
    users = await user_crud.get_users(db)
    return [User.model_validate(user) for user in users]


router.add_api_route(
    "/",
    list_users_endpoint,
    response_model=list[User],
    responses={
        200: {"description": "List of users"},
    },
    response_description="List of users",
    summary="List Users",
    description="Get a list of all users",
    operation_id="list_users",
    methods=["GET"],
)


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
    return await create_user(user_in, db)


async def create_user(
    user_in: UserCreate,
    db: DBSession,
) -> User:
    """
    Create new user.

    Args:
        user_in: The user data to create.
        db: The database session.

    Returns:
        The created user.

    Raises:
        HTTPException: If the email is already registered.
    """
    user = await user_crud.get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    db_user = await user_crud.create_user(db, user_in)
    return User.model_validate(db_user)


router.add_api_route(
    "/",
    create_user_endpoint,
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already registered"},
    },
    response_description="Created user",
    summary="Create User",
    description="Create a new user with the provided data",
    operation_id="create_user",
    methods=["POST"],
)


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


router.add_api_route(
    "/me",
    read_user_me_endpoint,
    response_model=User,
    responses={
        200: {"description": "Current user details"},
        404: {"description": "User not found"},
    },
    response_description="Current user",
    summary="Get Current User",
    description="Get details of the currently authenticated user",
    operation_id="read_user_me",
    methods=["GET"],
)


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
    user = await user_crud.get_user_by_email(db, form_data.username)
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
    user_id: str,
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
    # Check if user exists
    db_user = await user_crud.get_user_by_id(db, user_id)
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

    # Update user
    updated_user = await user_crud.update_user(db, db_user, user_update)
    return User.model_validate(updated_user)


@router.post("/{user_id}/deactivate", response_model=User)
async def deactivate_user_endpoint(
    user_id: str,
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
    # Only superusers can deactivate users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if user exists
    db_user = await user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Deactivate user
    user_update = UserUpdate(is_active=False)
    updated_user = await user_crud.update_user(db, db_user, user_update)
    return User.model_validate(updated_user)


@router.post("/me/change-password", response_model=User)
async def change_password_endpoint(
    password_change: PasswordChange,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: DBSession,
) -> User:
    """
    Change user password endpoint handler.

    Args:
        password_change: The password change data.
        current_user: The current authenticated user.
        db: The database session.

    Returns:
        The updated user.

    Raises:
        HTTPException: If the current password is incorrect.
    """
    # Verify current password
    is_valid = verify_password(
        password_change.current_password,
        current_user.hashed_password,
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Update password
    user_update = UserUpdate(password=password_change.new_password)
    updated_user = await user_crud.update_user(db, current_user, user_update)
    return User.model_validate(updated_user)
