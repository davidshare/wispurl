"""Request/response schemas for ``POST /check``."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CheckRequest(BaseModel):
    """A rate-limit check for one user performing one action.

    ``user_id`` is validated as a UUID and ``action`` is checked against the
    configured allow-list in the service layer; together these bound the set of
    keys that can ever be created in Redis.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: UUID
    action: str = Field(max_length=64)


class CheckResponse(BaseModel):
    """The outcome of a rate-limit check."""

    allowed: bool
    remaining: int
    reset_at: datetime
    limit: int
