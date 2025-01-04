from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DBSession, get_current_user
from app.crud import user as user_crud
from app.schemas.user import User, UserCreate

router = APIRouter()


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
    "",
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
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: DBSession,
) -> User:
    """
    Get current user endpoint handler.

    Args:
        current_user: The current user's data.
        db: The database session.

    Returns:
        The current user's details.

    Raises:
        HTTPException: If the user is not found.
    """
    return await read_user_me(current_user, db)


async def read_user_me(
    current_user: dict[str, Any],
    db: DBSession,
) -> User:
    """
    Get current user.

    Args:
        current_user: The current user's data.
        db: The database session.

    Returns:
        The current user's details.

    Raises:
        HTTPException: If the user is not found.
    """
    user = await user_crud.get_user_by_email(db, current_user["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return User.model_validate(user)


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
