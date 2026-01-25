"""Application configuration using pydantic-settings."""

import secrets
import warnings
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Minimum password length for admin password
MIN_ADMIN_PASSWORD_LENGTH = 12


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://perfwatch:perfwatch@db:5432/perfwatch"

    # JWT Authentication - no default, must be explicitly set
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # Admin User - no default password, must be explicitly set
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = ""

    # Application
    DEBUG: bool = False
    APP_NAME: str = "PerfWatch"
    APP_VERSION: str = "0.1.0"

    # Metrics Collection
    SAMPLING_INTERVAL_SECONDS: int = 5
    BACKGROUND_COLLECTION_ENABLED: bool = True
    RETENTION_CLEANUP_ENABLED: bool = True
    RETENTION_CLEANUP_INTERVAL_MINUTES: int = 60
    PERF_EVENTS_ENABLED: bool = True
    PERF_EVENTS_INTERVAL_MS: int = 1000
    PERF_EVENTS_CPU_CORES: str = "all"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT_SECRET is set and secure."""
        if not v:
            # Generate a secure random secret for development/testing
            generated = secrets.token_urlsafe(32)
            warnings.warn(
                "JWT_SECRET not set! A random secret has been generated. "
                "Set JWT_SECRET environment variable for production.",
                UserWarning,
                stacklevel=2,
            )
            return generated
        if len(v) < 32:
            warnings.warn(
                "JWT_SECRET should be at least 32 characters for security.",
                UserWarning,
                stacklevel=2,
            )
        if v == "change-this-in-production":
            warnings.warn(
                "Using default JWT_SECRET is insecure! Set a unique JWT_SECRET.",
                UserWarning,
                stacklevel=2,
            )
        return v

    @field_validator("ADMIN_PASSWORD")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        """Validate ADMIN_PASSWORD is set and meets minimum requirements."""
        if not v:
            # Generate a secure random password for development/testing
            generated = secrets.token_urlsafe(16)
            warnings.warn(
                f"ADMIN_PASSWORD not set! Generated password: {generated} "
                "Set ADMIN_PASSWORD environment variable for production.",
                UserWarning,
                stacklevel=2,
            )
            return generated
        if len(v) < MIN_ADMIN_PASSWORD_LENGTH:
            warnings.warn(
                f"ADMIN_PASSWORD should be at least {MIN_ADMIN_PASSWORD_LENGTH} characters.",
                UserWarning,
                stacklevel=2,
            )
        if v in ("admin123", "password", "admin", "123456"):
            warnings.warn(
                "Using a weak ADMIN_PASSWORD is insecure! Set a strong password.",
                UserWarning,
                stacklevel=2,
            )
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
