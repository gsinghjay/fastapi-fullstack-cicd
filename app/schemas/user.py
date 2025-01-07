"""User schemas."""
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# Constants
MIN_PASSWORD_LENGTH = 8


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False


class UserCreate(UserBase):
    """User creation schema."""

    email: EmailStr  # Override to make required
    password: Annotated[str, Field(min_length=MIN_PASSWORD_LENGTH)]
    is_active: bool = True  # Override to make required with default
    is_superuser: bool = False  # Override to make required with default


class UserUpdate(UserBase):
    """User update schema."""

    password: Annotated[str, Field(min_length=MIN_PASSWORD_LENGTH)] | None = None


class User(UserBase):
    """User response schema."""

    id: UUID
    email: EmailStr  # Override to make required
    is_active: bool  # Override to make required
    is_superuser: bool  # Override to make required

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
