from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ShortenerSettings
from app.errors.exceptions import (
    DuplicateShortCodeError,
    LinkNotFoundError,
    RateLimitExceededError,
    ShortCodeExhaustedError,
)
from app.models.link import Link
from app.repositories.link_repository import LinkRepository
from app.schemas.link import LinkListResponse, LinkResponse
from app.services.rate_limit import check_rate_limit
from app.services.shortcode import generate_random_shortcode, validate_custom_slug


class LinkService:
    def __init__(self, session: AsyncSession, settings: ShortenerSettings) -> None:
        self._session = session
        self._settings = settings
        self._links = LinkRepository(session)

    async def create_link(
        self,
        *,
        client: httpx.AsyncClient,
        user_id: UUID,
        long_url: str,
        custom_slug: str | None,
        expires_at: datetime | None,
    ) -> LinkResponse:
        if not await check_rate_limit(
            client=client,
            user_id=user_id,
            settings=self._settings,
        ):
            raise RateLimitExceededError

        short_code = (
            validate_custom_slug(custom_slug)
            if custom_slug is not None
            else await self._generate_available_shortcode()
        )

        try:
            link = await self._links.create(
                user_id=user_id,
                short_code=short_code,
                long_url=long_url,
                expires_at=expires_at,
            )
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            if custom_slug is not None:
                raise DuplicateShortCodeError from exc
            raise ShortCodeExhaustedError from exc

        return self._to_response(link)

    async def list_links(
        self,
        *,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> LinkListResponse:
        links, total = await self._links.list_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return LinkListResponse(
            items=[self._to_response(link) for link in links],
            limit=limit,
            offset=offset,
            total=total,
        )

    async def delete_link(self, *, user_id: UUID, link_id: UUID) -> None:
        link = await self._links.get_owned_by_id(link_id=link_id, user_id=user_id)
        if link is None:
            raise LinkNotFoundError
        await self._links.delete(link)
        await self._session.commit()

    async def resolve_link(self, *, short_code: str) -> Link:
        link = await self._links.get_by_short_code(short_code)
        if link is None or not link.is_active:
            raise LinkNotFoundError
        if link.expires_at is not None and link.expires_at <= datetime.now(UTC):
            raise LinkNotFoundError
        return link

    async def _generate_available_shortcode(self) -> str:
        for _ in range(self._settings.shortcode_max_retries):
            short_code = generate_random_shortcode(self._settings.shortcode_length)
            if not await self._links.short_code_exists(short_code):
                return short_code
        raise ShortCodeExhaustedError

    def _to_response(self, link: Link) -> LinkResponse:
        return LinkResponse(
            id=link.id,
            short_code=link.short_code,
            long_url=link.long_url,
            short_url=f"{self._settings.public_base_url_str}/{link.short_code}",
            created_at=link.created_at,
            expires_at=link.expires_at,
            is_active=link.is_active,
        )
