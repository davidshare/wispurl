from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ShortenerSettings, get_settings
from app.database import get_session
from app.security.auth import get_current_user_id

SettingsDep = Annotated[ShortenerSettings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
