"""create links

Revision ID: 20260616_0001
Revises:
Create Date: 2026-06-16 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260616_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("short_code", sa.String(length=32), nullable=False),
        sa.Column("long_url", sa.String(length=2048), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_links")),
        sa.UniqueConstraint("short_code", name=op.f("uq_links_short_code")),
    )
    op.create_index(op.f("ix_links_short_code"), "links", ["short_code"], unique=True)
    op.create_index(op.f("ix_links_user_id"), "links", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_links_user_id"), table_name="links")
    op.drop_index(op.f("ix_links_short_code"), table_name="links")
    op.drop_table("links")
