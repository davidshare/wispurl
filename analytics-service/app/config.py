"""Typed configuration for the analytics service.

All runtime configuration is read from the environment via :class:`AnalyticsSettings`.
Inherits ``jwt_secret``/``jwt_algorithm`` (with validators) from the shared
:class:`ServiceSettings` so that /stats token verification (AUTHZ option (a)) uses
the same secret and algorithm as every other service.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator

from shared.config import ServiceSettings


class AnalyticsSettings(ServiceSettings):
    """Environment-driven settings for the analytics process."""

    database_url: str = Field(alias="DATABASE_URL")

    # Shared secret presented by internal callers (the Shortener, later a queue
    # consumer) in the X-Internal-Key header. Required so click data cannot be forged.
    internal_api_key: str = Field(alias="INTERNAL_API_KEY")

    # Click-count thresholds that the notification flow (Prompt 8) will alert on.
    # Stored here so the value lives in config; analytics does not act on it yet.
    milestones: str = Field(default="100,1000,10000", alias="MILESTONES")

    top_referrers_limit: int = Field(default=5, alias="TOP_REFERRERS_LIMIT")
    max_referrer_length: int = Field(default=2048, alias="MAX_REFERRER_LENGTH")
    max_user_agent_length: int = Field(default=512, alias="MAX_USER_AGENT_LENGTH")

    cors_allowed_origins: str = Field(default="", alias="CORS_ALLOWED_ORIGINS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated CORS origins env value into a list."""
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def milestone_values(self) -> list[int]:
        """Parse the comma-separated MILESTONES env value into a sorted int list."""
        return sorted(
            int(value.strip())
            for value in self.milestones.split(",")
            if value.strip()
        )

    @field_validator("internal_api_key")
    @classmethod
    def validate_internal_api_key(cls, value: str) -> str:
        """Reject a weak internal key; it is the only guard on /events."""
        if len(value) < 16:
            msg = "INTERNAL_API_KEY must be at least 16 characters"
            raise ValueError(msg)
        return value

    @field_validator("top_referrers_limit")
    @classmethod
    def validate_top_referrers_limit(cls, value: int) -> int:
        """A non-positive top-N would make the referrers query meaningless."""
        if value < 1:
            msg = "TOP_REFERRERS_LIMIT must be at least 1"
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> AnalyticsSettings:
    """Return the process-wide settings singleton (parsed once, then cached)."""
    return AnalyticsSettings()
