"""Typed configuration for the QR code service.

All runtime configuration is read from the environment via :class:`QrSettings`. The
size bounds exist to cap resource usage: an unbounded image size is the main abuse
surface for a service that allocates pixel buffers.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field, field_validator, model_validator

from shared.config import ServiceSettings


class QrSettings(ServiceSettings):
    """Environment-driven settings for the QR process."""

    public_base_url: AnyHttpUrl = Field(alias="PUBLIC_BASE_URL")

    # Output image size bounds (square edge, in pixels). Requests are clamped/rejected
    # against these so a caller cannot ask for an enormous, memory-hungry image.
    min_size_px: int = Field(default=64, alias="MIN_SIZE_PX")
    max_size_px: int = Field(default=1024, alias="MAX_SIZE_PX")
    default_size_px: int = Field(default=256, alias="DEFAULT_SIZE_PX")

    # Cache lifetime (seconds) for the deterministic PNG responses.
    cache_ttl: int = Field(default=86400, alias="CACHE_TTL")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def public_base_url_str(self) -> str:
        """The configured base URL as a string without a trailing slash."""
        return str(self.public_base_url).rstrip("/")

    @field_validator("min_size_px", "max_size_px", "default_size_px")
    @classmethod
    def validate_positive_size(cls, value: int) -> int:
        """Sizes must be positive pixel counts."""
        if value < 1:
            msg = "Size bounds must be positive"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_size_ordering(self) -> QrSettings:
        """Ensure min <= default <= max so clamping is well defined."""
        if not self.min_size_px <= self.default_size_px <= self.max_size_px:
            msg = "Sizes must satisfy MIN_SIZE_PX <= DEFAULT_SIZE_PX <= MAX_SIZE_PX"
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> QrSettings:
    """Return the process-wide settings singleton (parsed once, then cached)."""
    return QrSettings()
