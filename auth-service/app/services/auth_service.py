from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AuthSettings
from app.errors.exceptions import (
    DuplicateUserError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import PublicUser
from app.schemas.token import TokenPair
from app.security.password import (
    hash_password,
    password_needs_rehash,
    run_dummy_verify,
    verify_password,
)
from app.security.tokens import (
    generate_refresh_token,
    hash_refresh_token,
    mint_access_token,
    refresh_token_expiry,
)

logger = structlog.get_logger()


class AuthService:
    def __init__(self, session: AsyncSession, settings: AuthSettings) -> None:
        self._session = session
        self._settings = settings
        self._users = UserRepository(session)
        self._refresh_tokens = RefreshTokenRepository(session)

    async def signup(self, *, email: str, password: str) -> PublicUser:
        # Argon2 is CPU-heavy; run it in a thread so it doesn't block the loop.
        hashed_password = await asyncio.to_thread(
            hash_password, password, self._settings
        )
        try:
            user = await self._users.create(
                email=email.lower(),
                hashed_password=hashed_password,
            )
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            # Keep the client response generic to reduce account enumeration signals.
            logger.warning("signup_duplicate")
            raise DuplicateUserError from exc
        logger.info("signup_succeeded", user_id=str(user.id))
        return PublicUser(id=user.id, email=user.email)

    async def login(self, *, email: str, password: str) -> TokenPair:
        user = await self._users.get_by_email(email.lower())
        if user is None:
            # Equalize timing against the real verify path; offload to a thread.
            await asyncio.to_thread(run_dummy_verify, password, self._settings)
            logger.warning("login_failed", reason="unknown_user")
            raise InvalidCredentialsError
        if not user.is_active:
            await asyncio.to_thread(run_dummy_verify, password, self._settings)
            logger.warning(
                "login_failed", reason="inactive_user", user_id=str(user.id)
            )
            raise InactiveUserError
        password_ok = await asyncio.to_thread(
            verify_password, password, user.hashed_password, self._settings
        )
        if not password_ok:
            logger.warning(
                "login_failed", reason="bad_password", user_id=str(user.id)
            )
            raise InvalidCredentialsError

        needs_rehash = await asyncio.to_thread(
            password_needs_rehash, user.hashed_password, self._settings
        )
        if needs_rehash:
            new_hash = await asyncio.to_thread(
                hash_password, password, self._settings
            )
            await self._users.update_password_hash(user, new_hash)

        token_pair = await self._issue_token_pair(user=user, family_id=None)
        await self._session.commit()
        logger.info("login_succeeded", user_id=str(user.id))
        return token_pair

    async def refresh(self, *, refresh_token: str) -> TokenPair:
        token_hash = hash_refresh_token(refresh_token, self._settings)
        stored_token = await self._refresh_tokens.get_by_hash(token_hash)
        if stored_token is None:
            raise InvalidRefreshTokenError

        if stored_token.revoked:
            # Reuse of an already-rotated token => likely theft; kill the family.
            await self._refresh_tokens.revoke_family(stored_token.family_id)
            await self._session.commit()
            logger.warning(
                "refresh_reuse_detected",
                user_id=str(stored_token.user_id),
                family_id=str(stored_token.family_id),
            )
            raise InvalidRefreshTokenError

        if stored_token.expires_at <= datetime.now(UTC):
            await self._refresh_tokens.revoke(stored_token)
            await self._session.commit()
            raise InvalidRefreshTokenError

        user = await self._users.get_by_id(stored_token.user_id)
        if user is None or not user.is_active:
            await self._refresh_tokens.revoke_family(stored_token.family_id)
            await self._session.commit()
            raise InvalidRefreshTokenError

        await self._refresh_tokens.revoke(stored_token)
        token_pair = await self._issue_token_pair(
            user=user,
            family_id=stored_token.family_id,
        )
        await self._session.commit()
        logger.info("refresh_succeeded", user_id=str(user.id))
        return token_pair

    async def logout(self, *, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token, self._settings)
        stored_token = await self._refresh_tokens.get_by_hash(token_hash)
        if stored_token is not None and not stored_token.revoked:
            await self._refresh_tokens.revoke(stored_token)
            logger.info("logout", user_id=str(stored_token.user_id))
        await self._session.commit()

    async def _issue_token_pair(
        self,
        *,
        user: User,
        family_id: UUID | None,
    ) -> TokenPair:
        raw_refresh_token = generate_refresh_token(self._settings)
        token_hash = hash_refresh_token(raw_refresh_token, self._settings)
        actual_family_id = family_id or uuid4()

        await self._refresh_tokens.create(
            user=user,
            family_id=actual_family_id,
            token_hash=token_hash,
            expires_at=refresh_token_expiry(self._settings),
        )

        return TokenPair(
            access_token=mint_access_token(str(user.id), self._settings),
            refresh_token=raw_refresh_token,
            expires_in=self._settings.access_token_ttl_minutes * 60,
        )
