# Multi-stage, uv-based, non-root. Build context is the qr-service/ directory; the
# shared/ package is vendored in, matching the other services. No Alembic/database.
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY shared/ ./shared/
COPY app/ ./app/
COPY entrypoint.sh README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.13-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --home /app app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    WEB_CONCURRENCY=2

WORKDIR /app
USER app

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
