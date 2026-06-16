from __future__ import annotations

import re
import secrets
import string

from app.errors.exceptions import InvalidSlugError

ALPHABET = string.digits + string.ascii_letters
CUSTOM_SLUG_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
SHORT_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
RESERVED_SLUGS = {
    "docs",
    "health",
    "links",
    "openapi.json",
    "redoc",
}


def generate_random_shortcode(length: int) -> str:
    """Use random base62 codes to avoid exposing total link counts."""

    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def validate_custom_slug(slug: str) -> str:
    normalized = slug.strip()
    if (
        not CUSTOM_SLUG_PATTERN.fullmatch(normalized)
        or normalized.casefold() in RESERVED_SLUGS
    ):
        raise InvalidSlugError
    return normalized


def validate_short_code_path(short_code: str) -> str:
    if (
        not SHORT_CODE_PATTERN.fullmatch(short_code)
        or short_code.casefold() in RESERVED_SLUGS
    ):
        raise InvalidSlugError
    return short_code
