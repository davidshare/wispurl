"""Typed configuration for the API gateway.

All runtime configuration is read from the environment via :class:`GatewaySettings`,
a Pydantic ``BaseSettings`` model. The gateway adds no secrets or magic numbers in
code: upstream service URLs, timeouts, CORS origins, and the JWT verification
parameters (inherited from the shared :class:`ServiceSettings`) all come from env.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field, field_validator

from shared.config import ServiceSettings

# Top-level path segments the bare ``GET /{short_code}`` catch-all must never
# match. They correspond to real gateway routes (or FastAPI's own docs routes)
# that are registered earlier; this set is an additional defensive guard so a
# short code can never be mistaken for one of them. Compared case-insensitively.
DEFAULT_RESERVED_PREFIXES: frozenset[str] = frozenset(
    {
        "auth",
        "links",
        "stats",
        "qr",
        "health",
        "docs",
        "redoc",
        "openapi.json",
    },
)


class GatewaySettings(ServiceSettings):
    """Environment-driven settings for the gateway process.

    Inherits ``jwt_secret`` and ``jwt_algorithm`` (with their validators) from
    :class:`shared.config.ServiceSettings`, so access-token verification uses the
    exact same secret and algorithm as every backend service.
    """

    auth_service_url: AnyHttpUrl = Field(alias="AUTH_SERVICE_URL")
    shortener_service_url: AnyHttpUrl = Field(alias="SHORTENER_SERVICE_URL")
    analytics_service_url: AnyHttpUrl = Field(alias="ANALYTICS_SERVICE_URL")
    qr_service_url: AnyHttpUrl = Field(alias="QR_SERVICE_URL")

    request_connect_timeout: float = Field(
        default=5.0,
        alias="REQUEST_CONNECT_TIMEOUT",
    )
    request_read_timeout: float = Field(
        default=30.0,
        alias="REQUEST_READ_TIMEOUT",
    )

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
    def reserved_prefixes(self) -> frozenset[str]:
        """Path segments the short-code catch-all must refuse to forward."""
        return DEFAULT_RESERVED_PREFIXES

    @field_validator("request_connect_timeout", "request_read_timeout")
    @classmethod
    def validate_positive_timeout(cls, value: float) -> float:
        """Reject non-positive timeouts; an unbounded proxy can hang forever."""
        if value <= 0:
            msg = "Upstream timeouts must be positive"
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> GatewaySettings:
    """Return the process-wide settings singleton (parsed once, then cached)."""
    return GatewaySettings()
