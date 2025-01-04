import uuid
from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """User creation schema."""

    password: Annotated[str, MinLen(8), MaxLen(100)]


class UserUpdate(UserBase):
    """User update schema."""

    password: Annotated[str, MinLen(8), MaxLen(100)] | None = None


class UserInDB(UserBase):
    """User DB schema."""

    id: uuid.UUID
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """User response schema."""

    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
