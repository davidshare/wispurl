from functools import lru_cache

from pydantic import AnyHttpUrl, Field, field_validator

from shared.config import ServiceSettings


class ShortenerSettings(ServiceSettings):
    database_url: str = Field(alias="DATABASE_URL")
    public_base_url: AnyHttpUrl = Field(alias="PUBLIC_BASE_URL")
    shortcode_length: int = Field(default=7, alias="SHORTCODE_LENGTH")
    shortcode_max_retries: int = Field(default=5, alias="SHORTCODE_MAX_RETRIES")
    rate_limiter_url: AnyHttpUrl = Field(alias="RATE_LIMITER_URL")
    analytics_service_url: AnyHttpUrl = Field(alias="ANALYTICS_SERVICE_URL")
    # Shared secret presented to the internal /events and /check endpoints.
    internal_api_key: str = Field(alias="INTERNAL_API_KEY")
    # Short timeout so a slow limiter cannot stall link creation.
    rate_limiter_request_timeout: float = Field(
        default=1.0,
        alias="RATE_LIMITER_REQUEST_TIMEOUT",
    )
    # If the limiter is unreachable, allow the create (fail-open) by default.
    rate_limiter_fail_open: bool = Field(default=True, alias="RATE_LIMITER_FAIL_OPEN")
    # Hard cap on the fire-and-forget analytics call so it can never slow a redirect.
    analytics_request_timeout: float = Field(
        default=2.0,
        alias="ANALYTICS_REQUEST_TIMEOUT",
    )
    cors_allowed_origins: str = Field(default="", alias="CORS_ALLOWED_ORIGINS")
    default_page_limit: int = Field(default=50, alias="DEFAULT_PAGE_LIMIT")
    max_page_limit: int = Field(default=100, alias="MAX_PAGE_LIMIT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def public_base_url_str(self) -> str:
        return str(self.public_base_url).rstrip("/")

    @field_validator("shortcode_length")
    @classmethod
    def validate_shortcode_length(cls, value: int) -> int:
        if value < 6 or value > 32:
            msg = "SHORTCODE_LENGTH must be between 6 and 32"
            raise ValueError(msg)
        return value

    @field_validator("shortcode_max_retries")
    @classmethod
    def validate_shortcode_max_retries(cls, value: int) -> int:
        if value < 1:
            msg = "SHORTCODE_MAX_RETRIES must be at least 1"
            raise ValueError(msg)
        return value

    @field_validator("default_page_limit", "max_page_limit")
    @classmethod
    def validate_positive_page_limit(cls, value: int) -> int:
        if value < 1:
            msg = "Pagination limits must be positive"
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> ShortenerSettings:
    return ShortenerSettings()
