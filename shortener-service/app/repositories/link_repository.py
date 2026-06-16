from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.link import Link


class LinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        short_code: str,
        long_url: str,
        expires_at: datetime | None,
    ) -> Link:
        link = Link(
            user_id=user_id,
            short_code=short_code,
            long_url=long_url,
            expires_at=expires_at,
        )
        self._session.add(link)
        await self._session.flush()
        await self._session.refresh(link)
        return link

    async def short_code_exists(self, short_code: str) -> bool:
        result = await self._session.execute(
            select(Link.id).where(Link.short_code == short_code),
        )
        return result.scalar_one_or_none() is not None

    async def get_by_short_code(self, short_code: str) -> Link | None:
        result = await self._session.execute(
            select(Link).where(Link.short_code == short_code),
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        *,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> tuple[list[Link], int]:
        base_query: Select[tuple[Link]] = (
            select(Link)
            .where(Link.user_id == user_id)
            .order_by(Link.created_at.desc(), Link.id.desc())
        )
        result = await self._session.execute(base_query.limit(limit).offset(offset))
        links = list(result.scalars().all())

        count_result = await self._session.execute(
            select(func.count()).select_from(Link).where(Link.user_id == user_id),
        )
        return links, count_result.scalar_one()

    async def get_owned_by_id(self, *, link_id: UUID, user_id: UUID) -> Link | None:
        result = await self._session.execute(
            select(Link).where(Link.id == link_id, Link.user_id == user_id),
        )
        return result.scalar_one_or_none()

    async def delete(self, link: Link) -> None:
        await self._session.delete(link)
        await self._session.flush()
