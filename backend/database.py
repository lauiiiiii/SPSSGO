# -*- coding: utf-8 -*-
"""数据库连接和仓储门面入口。

这里只放连接池、自举和仓储导出，别把业务编排和路由参数处理塞进来。
"""
import asyncio
import aiomysql
import json
from backend.config import (
    DB_AUTO_CREATE,
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE,
    MYSQL_POOL_MINSIZE, MYSQL_POOL_MAXSIZE,
)
from backend.domain import CREATED, PENDING

_pool: aiomysql.Pool | None = None
_pool_loop = None


async def _dispose_pool():
    global _pool, _pool_loop
    if _pool is None:
        _pool_loop = None
        return
    try:
        _pool.close()
        await _pool.wait_closed()
    except RuntimeError:
        # Celery workers may switch asyncio loops between tasks; if the old loop is
        # already closed we can only drop the stale pool reference and recreate it.
        pass
    finally:
        _pool = None
        _pool_loop = None


def _json_dumps(value):
    if value is None:
        return None
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _parse_json(value, default):
    if not value:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


def _normalize_job_row(row: dict | None) -> dict | None:
    if not row:
        return None
    item = dict(row)
    if "queue_name" in item:
        item["queue"] = item.pop("queue_name")
    item["payload"] = _parse_json(item.pop("payload_json", None), {})
    item["progress"] = _parse_json(item.pop("progress_json", None), {})
    item["result"] = _parse_json(item.pop("result_json", None), {})
    return item


def _normalize_sandbox_execution_row(row: dict | None) -> dict | None:
    if not row:
        return None
    item = dict(row)
    if "queue_name" in item:
        item["queue"] = item.pop("queue_name")
    item["details"] = _parse_json(item.pop("details_json", None), {})
    return item


async def _try_execute(cur, sql: str, params=None):
    try:
        await cur.execute(sql, params)
    except Exception:
        pass


async def _bootstrap_schema(cur):
    # Suppress MySQL "already exists" notes during idempotent startup bootstrap.
    await _try_execute(cur, "SET sql_notes = 0")
    try:
        await cur.execute("""
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
        """)
        await cur.execute("""
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
        """)
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key VARCHAR(128) PRIMARY KEY,
                setting_value LONGTEXT,
                updated_at DOUBLE NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await cur.execute(f"""
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
                status VARCHAR(32) DEFAULT '{CREATED}'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await cur.execute("""
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
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS shared_reports (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                share_token VARCHAR(64) NOT NULL UNIQUE,
                session_id VARCHAR(32) NULL,
                owner_id BIGINT NULL,
                payload_json LONGTEXT NOT NULL,
                expires_at DOUBLE NOT NULL,
                password_hash VARCHAR(500) NULL,
                created_at DOUBLE NOT NULL,
                INDEX idx_shared_reports_token (share_token),
                INDEX idx_shared_reports_session (session_id),
                INDEX idx_shared_reports_owner (owner_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await _try_execute(cur, "ALTER TABLE shared_reports ADD COLUMN expires_at DOUBLE NOT NULL DEFAULT 0 AFTER payload_json")
        await _try_execute(cur, "ALTER TABLE shared_reports ADD COLUMN password_hash VARCHAR(500) NULL AFTER expires_at")
        # 兼容旧表：自动添加 sections_json 列
        try:
            await cur.execute(
                "ALTER TABLE results ADD COLUMN sections_json MEDIUMTEXT AFTER description"
            )
        except Exception:
            pass
        await cur.execute("""
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
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                owner_id BIGINT NOT NULL,
                session_id VARCHAR(32) NOT NULL,
                name VARCHAR(255) NULL,
                original_filename VARCHAR(500) NOT NULL,
                storage_key VARCHAR(1000) NOT NULL,
                content_type VARCHAR(255),
                size_bytes BIGINT DEFAULT 0,
                current_version_id BIGINT NULL,
                created_at DOUBLE NOT NULL,
                last_used_at DOUBLE NULL,
                INDEX idx_dataset_owner (owner_id),
                UNIQUE KEY uniq_session_dataset (session_id),
                CONSTRAINT fk_dataset_user FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_dataset_session FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await cur.execute("""
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
        """)
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS dataset_folders (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                owner_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at DOUBLE NOT NULL,
                UNIQUE KEY uniq_dataset_folder_owner_name (owner_id, name),
                INDEX idx_dataset_folders_owner (owner_id),
                CONSTRAINT fk_dataset_folders_user FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS dataset_folder_items (
                folder_id BIGINT NOT NULL,
                dataset_id BIGINT NOT NULL,
                created_at DOUBLE NOT NULL,
                PRIMARY KEY (folder_id, dataset_id),
                UNIQUE KEY uniq_dataset_folder_item (dataset_id),
                INDEX idx_dataset_folder_items_folder (folder_id),
                CONSTRAINT fk_dataset_folder_items_folder FOREIGN KEY (folder_id) REFERENCES dataset_folders(id) ON DELETE CASCADE,
                CONSTRAINT fk_dataset_folder_items_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        await cur.execute(f"""
            CREATE TABLE IF NOT EXISTS jobs (
                id VARCHAR(32) PRIMARY KEY,
                job_type VARCHAR(64) NOT NULL,
                owner_id BIGINT NOT NULL,
                session_id VARCHAR(32) NULL,
                dataset_id BIGINT NULL,
                dataset_version_id BIGINT NULL,
                status VARCHAR(32) NOT NULL DEFAULT '{PENDING}',
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
        """)
        await cur.execute("""
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
        """)
        await _try_execute(cur, "ALTER TABLE sessions ADD COLUMN owner_id BIGINT NULL AFTER id")
        await _try_execute(cur, "ALTER TABLE sessions ADD COLUMN current_dataset_id BIGINT NULL AFTER owner_id")
        await _try_execute(cur, "ALTER TABLE sessions ADD COLUMN current_dataset_version_id BIGINT NULL AFTER current_dataset_id")
        await _try_execute(cur, "ALTER TABLE datasets ADD COLUMN name VARCHAR(255) NULL AFTER session_id")
        await _try_execute(cur, "ALTER TABLE datasets ADD COLUMN last_used_at DOUBLE NULL AFTER created_at")
        await _try_execute(cur, "ALTER TABLE dataset_versions ADD COLUMN name VARCHAR(255) NULL AFTER version_no")
        await _try_execute(cur, "ALTER TABLE results ADD COLUMN owner_id BIGINT NULL AFTER session_id")
        await _try_execute(cur, "ALTER TABLE results ADD COLUMN job_id VARCHAR(32) NULL AFTER owner_id")
        await _try_execute(cur, "ALTER TABLE results ADD COLUMN dataset_version_id BIGINT NULL AFTER job_id")
    finally:
        await _try_execute(cur, "SET sql_notes = 1")


async def init_db():
    global _pool, _pool_loop
    current_loop = asyncio.get_running_loop()
    if _pool is not None:
        if _pool_loop is current_loop:
            return
        await _dispose_pool()
    _pool = await aiomysql.create_pool(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DATABASE,
        charset="utf8mb4",
        autocommit=True,
        minsize=max(1, MYSQL_POOL_MINSIZE),
        maxsize=max(max(1, MYSQL_POOL_MINSIZE), MYSQL_POOL_MAXSIZE),
    )
    _pool_loop = current_loop
    if not DB_AUTO_CREATE:
        await bootstrap_initial_admin()
        return
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await _bootstrap_schema(cur)
    await bootstrap_initial_admin()


async def close_db():
    await _dispose_pool()


async def ping_db() -> bool:
    if _pool is None:
        return False
    try:
        async with _pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                row = await cur.fetchone()
        return bool(row)
    except Exception:
        return False


# 这里是兼容层，先别动导出名，外面一堆服务还在用。
from backend.repositories.result_repository import (
    delete_result,
    delete_results_for_job,
    get_results,
    rename_result,
    save_result,
)
from backend.repositories.session_repository import (
    cleanup_expired,
    create_session,
    delete_session,
    get_recent_sessions,
    get_session,
    get_session_for_user,
    update_session,
)
from backend.repositories.user_repository import (
    bootstrap_initial_admin,
    create_user,
    get_refresh_token,
    get_user_by_id,
    get_user_by_username,
    revoke_refresh_token,
    revoke_user_refresh_tokens,
    store_refresh_token,
    touch_user_last_login,
    update_user,
)

from backend.repositories.variable_metadata_repository import (
    delete_variable_metadata,
    get_variable_metadata_map,
    rename_variable_metadata,
    replace_variable_metadata,
    upsert_variable_metadata,
)
from backend.repositories.dataset_repository import (
    count_datasets_for_owner,
    create_dataset_version,
    get_current_dataset_version_for_session,
    get_dataset,
    get_dataset_for_session,
    get_dataset_version,
    list_datasets_for_owner,
    list_dataset_versions,
    update_dataset,
    update_dataset_version,
    upsert_dataset_for_session,
)
from backend.repositories.job_repository import (
    create_job,
    get_job,
    get_job_for_user,
    list_jobs_for_session,
    update_job,
)
from backend.repositories.sandbox_execution_repository import (
    cancel_active_sandbox_executions_for_job,
    create_sandbox_execution,
    get_sandbox_execution,
    list_sandbox_executions_for_job,
    update_sandbox_execution,
)

__all__ = [
    "close_db",
    "create_dataset_version",
    "count_datasets_for_owner",
    "create_job",
    "create_sandbox_execution",
    "create_session",
    "create_user",
    "delete_result",
    "delete_results_for_job",
    "delete_session",
    "delete_variable_metadata",
    "get_current_dataset_version_for_session",
    "get_dataset",
    "get_dataset_for_session",
    "get_dataset_version",
    "list_datasets_for_owner",
    "get_job",
    "get_job_for_user",
    "get_recent_sessions",
    "get_refresh_token",
    "get_results",
    "get_sandbox_execution",
    "get_session",
    "get_session_for_user",
    "get_user_by_id",
    "get_user_by_username",
    "get_variable_metadata_map",
    "init_db",
    "list_dataset_versions",
    "update_dataset_version",
    "list_jobs_for_session",
    "list_sandbox_executions_for_job",
    "ping_db",
    "rename_result",
    "rename_variable_metadata",
    "replace_variable_metadata",
    "revoke_refresh_token",
    "revoke_user_refresh_tokens",
    "save_result",
    "store_refresh_token",
    "touch_user_last_login",
    "update_dataset",
    "update_job",
    "update_sandbox_execution",
    "update_session",
    "update_user",
    "upsert_dataset_for_session",
    "upsert_variable_metadata",
    "bootstrap_initial_admin",
    "cleanup_expired",
    "cancel_active_sandbox_executions_for_job",
]
