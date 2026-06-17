"""Typed configuration for the cleanup service.

This service does no HTTP and no JWT work, so it reads a minimal settings set
directly from the environment rather than the shared (JWT-oriented) ServiceSettings.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CleanupSettings(BaseSettings):
    """Environment-driven settings for the cleanup loop."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    rabbitmq_url: str = Field(alias="RABBITMQ_URL")
    cleanup_interval_seconds: int = Field(
        default=60,
        alias="CLEANUP_INTERVAL_SECONDS",
    )
    batch_size: int = Field(default=500, alias="BATCH_SIZE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("cleanup_interval_seconds")
    @classmethod
    def validate_interval(cls, value: int) -> int:
        """A non-positive interval would busy-loop the sweep."""
        if value < 1:
            msg = "CLEANUP_INTERVAL_SECONDS must be at least 1"
            raise ValueError(msg)
        return value

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, value: int) -> int:
        """A non-positive batch size would deactivate nothing."""
        if value < 1:
            msg = "BATCH_SIZE must be at least 1"
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> CleanupSettings:
    """Return the process-wide settings singleton (parsed once, then cached)."""
    return CleanupSettings()
