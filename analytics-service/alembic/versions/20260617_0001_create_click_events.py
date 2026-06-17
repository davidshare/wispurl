"""create click_events

Revision ID: 20260617_0001
Revises:
Create Date: 2026-06-17 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260617_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "click_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("short_code", sa.String(length=32), nullable=False),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("referrer", sa.String(length=2048), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_click_events")),
    )
    op.create_index(
        op.f("ix_click_events_short_code"),
        "click_events",
        ["short_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_click_events_clicked_at"),
        "click_events",
        ["clicked_at"],
        unique=False,
    )
    op.create_index(
        "ix_click_events_short_code_clicked_at",
        "click_events",
        ["short_code", "clicked_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_click_events_short_code_clicked_at", table_name="click_events")
    op.drop_index(op.f("ix_click_events_clicked_at"), table_name="click_events")
    op.drop_index(op.f("ix_click_events_short_code"), table_name="click_events")
    op.drop_table("click_events")
