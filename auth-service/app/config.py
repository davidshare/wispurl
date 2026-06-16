from functools import lru_cache

from pydantic import Field, field_validator

from shared.config import ServiceSettings


class AuthSettings(ServiceSettings):
    database_url: str = Field(alias="DATABASE_URL")
    refresh_token_ttl_days: int = Field(default=7, alias="REFRESH_TOKEN_TTL_DAYS")
    refresh_token_bytes: int = Field(default=48, alias="REFRESH_TOKEN_BYTES")
    argon2_time_cost: int = Field(default=2, alias="ARGON2_TIME_COST")
    argon2_memory_cost: int = Field(default=19_456, alias="ARGON2_MEMORY_COST")
    argon2_parallelism: int = Field(default=1, alias="ARGON2_PARALLELISM")
    password_min_length: int = Field(default=12, alias="PASSWORD_MIN_LENGTH")
    password_max_length: int = Field(default=1024, alias="PASSWORD_MAX_LENGTH")
    cors_allowed_origins: str = Field(default="", alias="CORS_ALLOWED_ORIGINS")
    local_rate_limit_window_seconds: int = Field(
        default=60,
        alias="LOCAL_RATE_LIMIT_WINDOW_SECONDS",
    )
    local_rate_limit_max_requests: int = Field(
        default=20,
        alias="LOCAL_RATE_LIMIT_MAX_REQUESTS",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    @field_validator("argon2_memory_cost")
    @classmethod
    def validate_argon2_memory_cost(cls, value: int) -> int:
        if value < 19_456:
            msg = "ARGON2_MEMORY_COST must be at least 19456 KiB"
            raise ValueError(msg)
        return value

    @field_validator("argon2_time_cost")
    @classmethod
    def validate_argon2_time_cost(cls, value: int) -> int:
        if value < 2:
            msg = "ARGON2_TIME_COST must be at least 2"
            raise ValueError(msg)
        return value

    @field_validator("argon2_parallelism")
    @classmethod
    def validate_argon2_parallelism(cls, value: int) -> int:
        if value < 1:
            msg = "ARGON2_PARALLELISM must be at least 1"
            raise ValueError(msg)
        return value

    @field_validator("refresh_token_bytes")
    @classmethod
    def validate_refresh_token_bytes(cls, value: int) -> int:
        if value < 32:
            msg = "REFRESH_TOKEN_BYTES must be at least 32"
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> AuthSettings:
    return AuthSettings()
