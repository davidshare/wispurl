"""Typed configuration for the notification service.

No HTTP, no JWT — reads a minimal settings set directly from the environment.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NotificationSettings(BaseSettings):
    """Environment-driven settings for the notification consumer."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    rabbitmq_url: str = Field(alias="RABBITMQ_URL")

    # "log" (default): structured stdout. "smtp": send email (optional, see handlers).
    notify_channel: Literal["log", "smtp"] = Field(
        default="log",
        alias="NOTIFY_CHANNEL",
    )

    # Optional SMTP/Mailtrap settings, only used when notify_channel == "smtp".
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str | None = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, alias="SMTP_FROM")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> NotificationSettings:
    """Return the process-wide settings singleton (parsed once, then cached)."""
    return NotificationSettings()
