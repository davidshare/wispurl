"""Typed configuration for the rate limiter service.

All runtime configuration is read from the environment via :class:`RateLimiterSettings`.
Per-action limits are configured here; an action not present in :data:`action_limits`
is rejected, which also bounds Redis key cardinality.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator

from shared.config import ServiceSettings

# The only actions this service will rate-limit. Restricting to an allow-list keeps
# Redis key space bounded — arbitrary action strings can never create keys.
ACTION_CREATE_LINK = "create_link"


class RateLimiterSettings(ServiceSettings):
    """Environment-driven settings for the rate limiter process."""

    redis_url: str = Field(alias="REDIS_URL")

    # Shared secret presented by internal callers (the Shortener) in X-Internal-Key.
    internal_api_key: str = Field(alias="INTERNAL_API_KEY")

    # Fixed-window length and the per-window limit for create_link.
    window_seconds: int = Field(default=3600, alias="WINDOW_SECONDS")
    create_link_limit: int = Field(default=20, alias="CREATE_LINK_LIMIT")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def action_limits(self) -> dict[str, int]:
        """Map each allow-listed action to its per-window limit."""
        return {ACTION_CREATE_LINK: self.create_link_limit}

    @field_validator("window_seconds")
    @classmethod
    def validate_window_seconds(cls, value: int) -> int:
        """A non-positive window would make TTLs meaningless."""
        if value < 1:
            msg = "WINDOW_SECONDS must be at least 1"
            raise ValueError(msg)
        return value

    @field_validator("create_link_limit")
    @classmethod
    def validate_create_link_limit(cls, value: int) -> int:
        """A non-positive limit would reject every request."""
        if value < 1:
            msg = "CREATE_LINK_LIMIT must be at least 1"
            raise ValueError(msg)
        return value

    @field_validator("internal_api_key")
    @classmethod
    def validate_internal_api_key(cls, value: str) -> str:
        """Reject a weak internal key; it is the only guard on /check."""
        if len(value) < 16:
            msg = "INTERNAL_API_KEY must be at least 16 characters"
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> RateLimiterSettings:
    """Return the process-wide settings singleton (parsed once, then cached)."""
    return RateLimiterSettings()
