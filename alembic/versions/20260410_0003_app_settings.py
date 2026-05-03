"""add app settings table

Revision ID: 20260410_0003
Revises: 20260410_0002
Create Date: 2026-04-23 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260410_0003"
down_revision = "20260410_0002"
branch_labels = None
depends_on = None


def _safe_execute(sql: str) -> None:
    bind = op.get_bind()
    try:
        bind.execute(sa.text(sql))
    except Exception:
        pass


def upgrade() -> None:
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key VARCHAR(128) PRIMARY KEY,
            setting_value LONGTEXT,
            updated_at DOUBLE NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )


def downgrade() -> None:
    _safe_execute("DROP TABLE IF EXISTS app_settings")
