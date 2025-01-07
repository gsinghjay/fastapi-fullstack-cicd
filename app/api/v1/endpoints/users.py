from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DBSession, get_current_user
from app.core.security import create_access_token, verify_password
from app.crud import user as user_crud
from app.models.user import User as UserModel
from app.schemas.user import Token, User, UserCreate

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
