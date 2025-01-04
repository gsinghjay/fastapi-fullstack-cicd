from typing import Annotated

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    VERSION: str = "0.1.0"
    APP_NAME: str = "FastAPI App"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = Field(
        default=[
            AnyHttpUrl("http://localhost:3000"),
            AnyHttpUrl("http://localhost:8000"),
        ],
        description="List of origins that can make cross-origin requests.",
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: str | list[str]) -> list[str] | str:
        """
        Validate and assemble CORS origins.

        Args:
            value: The CORS origins value from environment.

        Returns:
            The processed CORS origins.

        Raises:
            ValueError: If the value is invalid.
        """
        if isinstance(value, str) and not value.startswith("["):
            return [i.strip() for i in value.split(",")]
        if isinstance(value, str | list):
            return value
        raise ValueError(value)

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/app",
        description="Database connection URL.",
    )

    # JWT Authentication
    SECRET_KEY: Annotated[str, Field(min_length=32)] = Field(
        default="your-secret-key-here",
        description="Secret key for JWT token encoding.",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: Annotated[int, Field(gt=0)] = Field(
        default=30,
        description="Number of minutes after which access tokens expire.",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for JWT token encoding.",
        pattern="^(HS256|HS384|HS512|RS256|RS384|RS512|ES256|ES384|ES512|PS256|PS384|PS512)$",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        validate_default=True,
        extra="allow",
    )


# Create global settings instance
settings = Settings()
