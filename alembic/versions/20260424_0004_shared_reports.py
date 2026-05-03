"""add shared reports table

Revision ID: 20260424_0004
Revises: 20260410_0003
Create Date: 2026-04-24 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260424_0004"
down_revision = "20260410_0003"
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
        CREATE TABLE IF NOT EXISTS shared_reports (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            share_token VARCHAR(64) NOT NULL UNIQUE,
            session_id VARCHAR(32) NULL,
            owner_id BIGINT NULL,
            payload_json LONGTEXT NOT NULL,
            created_at DOUBLE NOT NULL,
            INDEX idx_shared_reports_token (share_token),
            INDEX idx_shared_reports_session (session_id),
            INDEX idx_shared_reports_owner (owner_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )


def downgrade() -> None:
    _safe_execute("DROP TABLE IF EXISTS shared_reports")
