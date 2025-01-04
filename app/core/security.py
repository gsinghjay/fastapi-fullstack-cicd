from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict[str, Any]) -> str:
    """
    Create JWT access token.

    Args:
        data: The data to encode in the token.

    Returns:
        The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode JWT access token.

    Args:
        token: The JWT token to decode.

    Returns:
        The decoded token data or None if invalid.
    """
    try:
        decoded_token: dict[str, Any] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        return decoded_token
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: The plain text password.
        hashed_password: The hashed password to verify against.

    Returns:
        True if the password matches, False otherwise.
    """
    is_valid: bool = pwd_context.verify(plain_password, hashed_password)
    return is_valid


def get_password_hash(password: str) -> str:
    """
    Get password hash.

    Args:
        password: The password to hash.

    Returns:
        The hashed password.
    """
    hashed_password: str = pwd_context.hash(password)
    return hashed_password
