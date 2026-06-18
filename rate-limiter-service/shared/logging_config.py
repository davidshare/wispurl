import logging
import sys
from typing import Any

import structlog

# Keys whose values are redacted wherever they appear (top-level or nested).
SECRET_KEYS = {
    "access_token",
    "api_key",
    "authorization",
    "cookie",
    "internal_api_key",
    "jwt_secret",
    "password",
    "refresh_token",
    "secret",
    "set-cookie",
    "smtp_password",
    "token",
    "x-internal-key",
}


def _scrub_value(value: Any) -> Any:
    """Recurse into dicts/lists, redacting any value under a secret-named key."""
    if isinstance(value, dict):
        return {
            key: ("[redacted]" if key.lower() in SECRET_KEYS else _scrub_value(val))
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [_scrub_value(item) for item in value]
    return value


def _scrub_secrets(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """structlog processor: redact secret-named keys, recursing into nested values."""
    for key in list(event_dict):
        if key.lower() in SECRET_KEYS:
            event_dict[key] = "[redacted]"
        else:
            event_dict[key] = _scrub_value(event_dict[key])
    return event_dict


def configure_logging(service_name: str, log_level: str = "INFO") -> None:
    """Configure JSON logs with request_id-friendly context binding."""

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _scrub_secrets,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.EventRenamer("message"),
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level.upper(),
        force=True,
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper()),
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    structlog.contextvars.bind_contextvars(service=service_name)


def bind_request_id(request_id: str | None) -> None:
    if request_id:
        structlog.contextvars.bind_contextvars(request_id=request_id)


def clear_request_context() -> None:
    structlog.contextvars.clear_contextvars()
