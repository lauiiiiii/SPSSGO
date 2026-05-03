"""add sandbox execution audit table

Revision ID: 20260410_0002
Revises: 20260410_0001
Create Date: 2026-04-10 16:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260410_0002"
down_revision = "20260410_0001"
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
        CREATE TABLE IF NOT EXISTS sandbox_executions (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            execution_id VARCHAR(32) NOT NULL UNIQUE,
            job_id VARCHAR(32) NOT NULL,
            owner_id BIGINT NOT NULL,
            session_id VARCHAR(32) NULL,
            dataset_version_id BIGINT NULL,
            celery_task_id VARCHAR(255) NULL,
            queue_name VARCHAR(32) NOT NULL DEFAULT 'sandbox',
            status VARCHAR(32) NOT NULL DEFAULT 'queued',
            executor_mode VARCHAR(32) NULL,
            docker_image VARCHAR(255) NULL,
            container_name VARCHAR(255) NULL,
            data_storage_key VARCHAR(1000) NULL,
            created_at DOUBLE NOT NULL,
            started_at DOUBLE NULL,
            finished_at DOUBLE NULL,
            duration_ms BIGINT NULL,
            exit_code INT NULL,
            error_message TEXT,
            details_json LONGTEXT,
            INDEX idx_sandbox_job (job_id),
            INDEX idx_sandbox_session (session_id),
            INDEX idx_sandbox_status (status),
            CONSTRAINT fk_sandbox_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            CONSTRAINT fk_sandbox_user FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_sandbox_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )


def downgrade() -> None:
    _safe_execute("DROP TABLE IF EXISTS sandbox_executions")
