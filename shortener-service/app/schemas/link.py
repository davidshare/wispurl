from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

MAX_URL_LENGTH = 2048


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CreateLinkRequest(StrictModel):
    long_url: AnyHttpUrl = Field(max_length=MAX_URL_LENGTH)
    custom_slug: str | None = Field(default=None, min_length=3, max_length=32)
    expires_at: datetime | None = None

    @field_validator("long_url")
    @classmethod
    def validate_http_url(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        # Restrict to http/https so the (intentional) redirect cannot deliver a
        # javascript:/data:/file:/ftp: payload to the end user's browser. This is
        # the security boundary that makes the open-redirect-by-design safe; see
        # the redirect route for the full open-redirect/SSRF rationale.
        if value.scheme not in {"http", "https"}:
            msg = "URL must use http or https"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_expiry(self) -> CreateLinkRequest:
        if self.expires_at is not None:
            if self.expires_at.tzinfo is None:
                msg = "expires_at must include a timezone"
                raise ValueError(msg)
            if self.expires_at <= datetime.now(UTC):
                msg = "expires_at must be in the future"
                raise ValueError(msg)
        return self


class LinkResponse(StrictModel):
    id: UUID
    short_code: str
    long_url: str
    short_url: str
    created_at: datetime
    expires_at: datetime | None
    is_active: bool


class LinkListResponse(StrictModel):
    items: list[LinkResponse]
    limit: int
    offset: int
    total: int
