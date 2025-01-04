from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    VERSION: str = "0.1.0"
    APP_NAME: str = "FastAPI App"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

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
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, validate_default=True, extra="allow"
    )


# Create global settings instance
settings = Settings()
