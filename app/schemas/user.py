from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Shared properties for user schemas."""

    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    """Properties to receive via API on creation."""

    password: str


class UserUpdate(UserBase):
    """Properties to receive via API on update."""

    password: str | None = None


class UserInDBBase(UserBase):
    """Properties shared by models stored in DB."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class User(UserInDBBase):
    """Additional properties to return via API."""

    pass


class UserInDB(UserInDBBase):
    """Additional properties stored in DB."""

    hashed_password: str
