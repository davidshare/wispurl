"""Query-parameter schema for ``GET /qr/{short_code}``."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QrQuery(BaseModel):
    """Validated query parameters for a QR request.

    ``extra="forbid"`` rejects unknown query params. ``size`` is bound-checked
    against the configured min/max in the route (the bounds are configurable, so
    they cannot live as static field constraints here); ``ge=1`` cheaply rejects
    zero/negative values up front. Only PNG output is supported.
    """

    model_config = ConfigDict(extra="forbid")

    size: int | None = Field(default=None, ge=1)
    format: Literal["png"] = "png"
