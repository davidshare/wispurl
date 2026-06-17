"""Shared FastAPI dependencies for the analytics service."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AnalyticsSettings, get_settings
from app.database import get_session
from app.security.auth import get_current_user_id

SettingsDep = Annotated[AnalyticsSettings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
# Identity of the authenticated caller for /stats (AUTHZ option (a)).
CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
# Note: /events gates on the internal key via Depends(require_internal_key) declared
# directly on the route (see app/routes/events.py), not through an alias here.
