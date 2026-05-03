"""add shared report expiry and password

Revision ID: 20260424_0005
Revises: 20260424_0004
Create Date: 2026-04-24 00:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260424_0005"
down_revision = "20260424_0004"
branch_labels = None
depends_on = None


def _safe_execute(sql: str) -> None:
    bind = op.get_bind()
    try:
        bind.execute(sa.text(sql))
    except Exception:
        pass


def upgrade() -> None:
    _safe_execute("ALTER TABLE shared_reports ADD COLUMN expires_at DOUBLE NOT NULL DEFAULT 0 AFTER payload_json")
    _safe_execute("ALTER TABLE shared_reports ADD COLUMN password_hash VARCHAR(500) NULL AFTER expires_at")


def downgrade() -> None:
    _safe_execute("ALTER TABLE shared_reports DROP COLUMN password_hash")
    _safe_execute("ALTER TABLE shared_reports DROP COLUMN expires_at")
