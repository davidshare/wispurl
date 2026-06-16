from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    """Base settings class every service can subclass."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_ttl_minutes: int = Field(
        default=15,
        alias="ACCESS_TOKEN_TTL_MINUTES",
    )
    refresh_token_ttl_days: int = Field(default=7, alias="REFRESH_TOKEN_TTL_DAYS")

    redis_url: str = Field(alias="REDIS_URL")
    rabbitmq_url: str = Field(alias="RABBITMQ_URL")

    auth_service_url: str = Field(alias="AUTH_SERVICE_URL")
    shortener_service_url: str = Field(alias="SHORTENER_SERVICE_URL")
    analytics_service_url: str = Field(alias="ANALYTICS_SERVICE_URL")
    rate_limiter_url: str = Field(alias="RATE_LIMITER_URL")
    qr_service_url: str = Field(alias="QR_SERVICE_URL")
