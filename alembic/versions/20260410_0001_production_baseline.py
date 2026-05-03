"""production baseline schema

Revision ID: 20260410_0001
Revises:
Create Date: 2026-04-10 12:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260410_0001"
down_revision = None
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
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(500) NOT NULL,
            role VARCHAR(32) NOT NULL DEFAULT 'user',
            is_active TINYINT NOT NULL DEFAULT 1,
            created_at DOUBLE NOT NULL,
            last_login_at DOUBLE NULL,
            INDEX idx_users_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            token_hash CHAR(64) NOT NULL UNIQUE,
            expires_at DOUBLE NOT NULL,
            created_at DOUBLE NOT NULL,
            revoked_at DOUBLE NULL,
            INDEX idx_refresh_user (user_id),
            INDEX idx_refresh_exp (expires_at),
            CONSTRAINT fk_refresh_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id VARCHAR(32) PRIMARY KEY,
            owner_id BIGINT NULL,
            current_dataset_id BIGINT NULL,
            current_dataset_version_id BIGINT NULL,
            created_at DOUBLE NOT NULL,
            research_topic TEXT,
            variable_desc TEXT,
            hypotheses TEXT,
            analysis_request TEXT,
            questionnaire_text MEDIUMTEXT,
            data_summary MEDIUMTEXT,
            plan MEDIUMTEXT,
            plan_confirmed TINYINT DEFAULT 0,
            status VARCHAR(32) DEFAULT 'created'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INT PRIMARY KEY AUTO_INCREMENT,
            session_id VARCHAR(32) NOT NULL,
            owner_id BIGINT NULL,
            job_id VARCHAR(32) NULL,
            dataset_version_id BIGINT NULL,
            analysis_name VARCHAR(500) NOT NULL,
            table_headers MEDIUMTEXT,
            table_rows MEDIUMTEXT,
            description TEXT,
            sections_json MEDIUMTEXT,
            code MEDIUMTEXT,
            created_at DOUBLE NOT NULL,
            INDEX idx_session_id (session_id),
            CONSTRAINT fk_results_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS variable_metadata (
            id INT PRIMARY KEY AUTO_INCREMENT,
            session_id VARCHAR(32) NOT NULL,
            variable_name VARCHAR(255) NOT NULL,
            var_type VARCHAR(32),
            display_name VARCHAR(255),
            value_labels_json MEDIUMTEXT,
            code_rules_json MEDIUMTEXT,
            updated_at DOUBLE NOT NULL,
            UNIQUE KEY uniq_session_variable (session_id, variable_name),
            INDEX idx_vm_session (session_id),
            CONSTRAINT fk_variable_metadata_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS datasets (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            owner_id BIGINT NOT NULL,
            session_id VARCHAR(32) NOT NULL,
            original_filename VARCHAR(500) NOT NULL,
            storage_key VARCHAR(1000) NOT NULL,
            content_type VARCHAR(255),
            size_bytes BIGINT DEFAULT 0,
            current_version_id BIGINT NULL,
            created_at DOUBLE NOT NULL,
            INDEX idx_dataset_owner (owner_id),
            UNIQUE KEY uniq_session_dataset (session_id),
            CONSTRAINT fk_dataset_user FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_dataset_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS dataset_versions (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            dataset_id BIGINT NOT NULL,
            owner_id BIGINT NOT NULL,
            session_id VARCHAR(32) NOT NULL,
            version_no INT NOT NULL,
            source_job_id VARCHAR(32) NULL,
            storage_key VARCHAR(1000) NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'ready',
            summary_json MEDIUMTEXT,
            preview_json MEDIUMTEXT,
            schema_json MEDIUMTEXT,
            created_at DOUBLE NOT NULL,
            INDEX idx_dataset_versions_dataset (dataset_id),
            INDEX idx_dataset_versions_session (session_id),
            UNIQUE KEY uniq_dataset_version (dataset_id, version_no),
            CONSTRAINT fk_dataset_versions_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
            CONSTRAINT fk_dataset_versions_user FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    _safe_execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id VARCHAR(32) PRIMARY KEY,
            job_type VARCHAR(64) NOT NULL,
            owner_id BIGINT NOT NULL,
            session_id VARCHAR(32) NULL,
            dataset_id BIGINT NULL,
            dataset_version_id BIGINT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            queue_name VARCHAR(32) NOT NULL,
            payload_json LONGTEXT,
            progress_json MEDIUMTEXT,
            result_json MEDIUMTEXT,
            attempts INT NOT NULL DEFAULT 0,
            error_message TEXT,
            celery_task_id VARCHAR(255),
            created_at DOUBLE NOT NULL,
            started_at DOUBLE NULL,
            finished_at DOUBLE NULL,
            INDEX idx_jobs_owner (owner_id),
            INDEX idx_jobs_session (session_id),
            INDEX idx_jobs_status (status),
            CONSTRAINT fk_jobs_user FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_jobs_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    _safe_execute("ALTER TABLE sessions ADD COLUMN owner_id BIGINT NULL AFTER id")
    _safe_execute("ALTER TABLE sessions ADD COLUMN current_dataset_id BIGINT NULL AFTER owner_id")
    _safe_execute("ALTER TABLE sessions ADD COLUMN current_dataset_version_id BIGINT NULL AFTER current_dataset_id")
    _safe_execute("ALTER TABLE results ADD COLUMN owner_id BIGINT NULL AFTER session_id")
    _safe_execute("ALTER TABLE results ADD COLUMN job_id VARCHAR(32) NULL AFTER owner_id")
    _safe_execute("ALTER TABLE results ADD COLUMN dataset_version_id BIGINT NULL AFTER job_id")
    _safe_execute("ALTER TABLE results ADD COLUMN sections_json MEDIUMTEXT AFTER description")


def downgrade() -> None:
    _safe_execute("DROP TABLE IF EXISTS jobs")
    _safe_execute("DROP TABLE IF EXISTS dataset_versions")
    _safe_execute("DROP TABLE IF EXISTS datasets")
    _safe_execute("DROP TABLE IF EXISTS variable_metadata")
    _safe_execute("DROP TABLE IF EXISTS results")
    _safe_execute("DROP TABLE IF EXISTS refresh_tokens")
    _safe_execute("DROP TABLE IF EXISTS sessions")
    _safe_execute("DROP TABLE IF EXISTS users")
