"""grant the cleanup worker least-privilege access to links

The cleanup worker connects as its own role (cleanup_svc, created by
db/init/create-service-roles.sh). It only needs to find expired links and mark
them inactive, so it gets exactly those columns. The grant lives here, with the
table, so a fresh database gets it as soon as the table exists.

Revision ID: 20261017_0003
Revises: 20260618_0002
Create Date: 2026-10-17 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "20261017_0003"
down_revision: str | None = "20260618_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Skipped when the role doesn't exist (for example in a database without the
# service roles), so the migration never fails on its own.
_GRANT = """
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'cleanup_svc') THEN
    GRANT USAGE ON SCHEMA public TO cleanup_svc;
    GRANT SELECT (id, short_code, is_active, expires_at), UPDATE (is_active)
      ON links TO cleanup_svc;
  END IF;
END
$$;
"""

_REVOKE = """
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'cleanup_svc') THEN
    REVOKE ALL ON links FROM cleanup_svc;
  END IF;
END
$$;
"""


def upgrade() -> None:
    op.execute(_GRANT)


def downgrade() -> None:
    op.execute(_REVOKE)
