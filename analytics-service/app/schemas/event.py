"""Request schema for internal click ingestion (``POST /events``)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# Bounds mirror the column widths in app/models/click_event.py so validation
# rejects oversized input before it can reach (and bloat) the database.
SHORT_CODE_PATTERN = r"^[A-Za-z0-9_-]{1,32}$"
MAX_IP_LENGTH = 64
MAX_REFERRER_LENGTH = 2048
MAX_USER_AGENT_LENGTH = 512


class RecordClickRequest(BaseModel):
    """One click reported by an internal caller (the Shortener).

    ``extra="forbid"`` rejects unexpected fields. ``ip_address`` is whatever the
    caller observed; it is anonymized by the service before storage, never stored raw.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    short_code: str = Field(pattern=SHORT_CODE_PATTERN)
    ip_address: str | None = Field(default=None, max_length=MAX_IP_LENGTH)
    referrer: str | None = Field(default=None, max_length=MAX_REFERRER_LENGTH)
    user_agent: str | None = Field(default=None, max_length=MAX_USER_AGENT_LENGTH)
    clicked_at: datetime | None = None
