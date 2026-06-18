"""add partial index for the cleanup expiry sweep

Revision ID: 20260618_0002
Revises: 20260616_0001
Create Date: 2026-06-18 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

revision: str = "20260618_0002"
down_revision: str | None = "20260616_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Supports the Cleanup service sweep: WHERE is_active AND expires_at < now().
    # Partial (WHERE is_active) keeps it small — only live, expiring links.
    op.create_index(
        "ix_links_active_expiry",
        "links",
        ["expires_at"],
        unique=False,
        postgresql_where=text("is_active"),
    )


def downgrade() -> None:
    op.drop_index("ix_links_active_expiry", table_name="links")
