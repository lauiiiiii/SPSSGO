# -*- coding: utf-8 -*-
"""管理后台的数据查询层，只放 SQL 读写，别塞业务判断。"""
import aiomysql
import time

import backend.database as db
from backend.domain import ACTIVE_JOB_STATUSES, DONE, EXECUTING


async def get_dashboard_stats():
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = (await cur.fetchone())[0]
            await cur.execute("SELECT COUNT(*) FROM sessions WHERE status=%s", (DONE,))
            done_sessions = (await cur.fetchone())[0]
            await cur.execute("SELECT COUNT(*) FROM sessions WHERE status=%s", (EXECUTING,))
            active_sessions = (await cur.fetchone())[0]
            await cur.execute("SELECT COUNT(*) FROM results")
            total_results = (await cur.fetchone())[0]
            await cur.execute(
                "SELECT DATE(FROM_UNIXTIME(created_at)) as d, COUNT(*) as c "
                "FROM sessions GROUP BY d ORDER BY d DESC LIMIT 7"
            )
            daily_sessions = [{"date": str(row[0]), "count": row[1]} for row in await cur.fetchall()]

    return {
        "total_sessions": total_sessions,
        "done_sessions": done_sessions,
        "active_sessions": active_sessions,
        "total_results": total_results,
        "daily_sessions": daily_sessions,
    }


async def list_admin_sessions(page: int, size: int):
    offset = (page - 1) * size
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM sessions")
            total = (await cur.fetchone())[0]

        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, created_at, research_topic, status FROM sessions "
                "ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (size, offset),
            )
            rows = await cur.fetchall()

        async with conn.cursor() as cur:
            session_ids = [row["id"] for row in rows]
            result_counts = {}
            if session_ids:
                placeholders = ",".join(["%s"] * len(session_ids))
                await cur.execute(
                    f"SELECT session_id, COUNT(*) FROM results WHERE session_id IN ({placeholders}) GROUP BY session_id",
                    session_ids,
                )
                for sid, cnt in await cur.fetchall():
                    result_counts[sid] = cnt

    sessions = []
    for row in rows:
        item = dict(row)
        item["result_count"] = result_counts.get(row["id"], 0)
        sessions.append(item)

    return {"total": total, "page": page, "size": size, "sessions": sessions}


async def delete_session_records(session_id: str):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM results WHERE session_id = %s", (session_id,))
            await cur.execute("DELETE FROM sessions WHERE id = %s", (session_id,))


async def get_app_settings(keys: list[str]) -> dict[str, str]:
    if not keys:
        return {}
    placeholders = ",".join(["%s"] * len(keys))
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT setting_key, setting_value FROM app_settings WHERE setting_key IN ({placeholders})",
                keys,
            )
            rows = await cur.fetchall()
    return {key: value for key, value in rows}


async def save_app_settings(settings: dict[str, str]) -> None:
    if not settings:
        return
    now = time.time()
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            for key, value in settings.items():
                await cur.execute(
                    """
                    INSERT INTO app_settings (setting_key, setting_value, updated_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), updated_at = VALUES(updated_at)
                    """,
                    (key, value, now),
                )


def _build_filter_clause(filters: list[tuple[str, object]]):
    if not filters:
        return "", []
    return " WHERE " + " AND ".join(item[0] for item in filters), [item[1] for item in filters]


async def get_admin_operations_summary():
    job_status_counts = {}
    job_queue_counts = {}
    sandbox_status_counts = {}
    sandbox_mode_counts = {}
    cutoff = time.time() - 24 * 3600

    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            for status, count in await cur.fetchall():
                job_status_counts[status] = count

            placeholders = ",".join(["%s"] * len(ACTIVE_JOB_STATUSES))
            await cur.execute(
                f"SELECT queue_name, COUNT(*) FROM jobs WHERE status IN ({placeholders}) GROUP BY queue_name",
                list(ACTIVE_JOB_STATUSES),
            )
            for queue_name, count in await cur.fetchall():
                job_queue_counts[queue_name] = count

            await cur.execute("SELECT status, COUNT(*) FROM sandbox_executions GROUP BY status")
            for status, count in await cur.fetchall():
                sandbox_status_counts[status] = count

            await cur.execute(
                "SELECT COALESCE(executor_mode, 'unknown') AS executor_mode, COUNT(*) FROM sandbox_executions GROUP BY executor_mode"
            )
            for executor_mode, count in await cur.fetchall():
                sandbox_mode_counts[executor_mode] = count

            await cur.execute("SELECT COUNT(*) FROM jobs WHERE created_at >= %s", (cutoff,))
            jobs_last_24h = (await cur.fetchone())[0]
            await cur.execute(
                "SELECT COUNT(*) FROM sandbox_executions WHERE created_at >= %s AND status = %s",
                (cutoff, "failed"),
            )
            sandbox_failures_last_24h = (await cur.fetchone())[0]

    return {
        "job_status_counts": job_status_counts,
        "job_queue_counts": job_queue_counts,
        "sandbox_status_counts": sandbox_status_counts,
        "sandbox_mode_counts": sandbox_mode_counts,
        "jobs_last_24h": jobs_last_24h,
        "sandbox_failures_last_24h": sandbox_failures_last_24h,
    }


async def list_admin_jobs(page: int, size: int, *, status: str = "", queue: str = "", job_type: str = ""):
    offset = (page - 1) * size
    filters: list[tuple[str, object]] = []
    if status:
        filters.append(("j.status = %s", status))
    if queue:
        filters.append(("j.queue_name = %s", queue))
    if job_type:
        filters.append(("j.job_type = %s", job_type))
    where_clause, where_params = _build_filter_clause(filters)

    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT COUNT(*) FROM jobs j{where_clause}", where_params)
            total = (await cur.fetchone())[0]

        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"""
                SELECT
                    j.id,
                    j.job_type,
                    j.status,
                    j.queue_name,
                    j.session_id,
                    j.dataset_version_id,
                    j.attempts,
                    j.error_message,
                    j.created_at,
                    j.started_at,
                    j.finished_at,
                    u.username AS owner_username
                FROM jobs j
                LEFT JOIN users u ON u.id = j.owner_id
                {where_clause}
                ORDER BY j.created_at DESC
                LIMIT %s OFFSET %s
                """,
                where_params + [size, offset],
            )
            rows = await cur.fetchall()

    return {"total": total, "page": page, "size": size, "jobs": [dict(row) for row in rows]}


async def list_admin_sandbox_executions(
    page: int,
    size: int,
    *,
    status: str = "",
    executor_mode: str = "",
):
    offset = (page - 1) * size
    filters: list[tuple[str, object]] = []
    if status:
        filters.append(("s.status = %s", status))
    if executor_mode:
        filters.append(("COALESCE(s.executor_mode, 'unknown') = %s", executor_mode))
    where_clause, where_params = _build_filter_clause(filters)

    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT COUNT(*) FROM sandbox_executions s{where_clause}", where_params)
            total = (await cur.fetchone())[0]

        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"""
                SELECT
                    s.execution_id,
                    s.job_id,
                    s.status,
                    s.queue_name,
                    s.executor_mode,
                    s.docker_image,
                    s.container_name,
                    s.session_id,
                    s.dataset_version_id,
                    s.created_at,
                    s.started_at,
                    s.finished_at,
                    s.duration_ms,
                    s.exit_code,
                    s.error_message,
                    u.username AS owner_username,
                    j.job_type
                FROM sandbox_executions s
                LEFT JOIN jobs j ON j.id = s.job_id
                LEFT JOIN users u ON u.id = s.owner_id
                {where_clause}
                ORDER BY s.created_at DESC
                LIMIT %s OFFSET %s
                """,
                where_params + [size, offset],
            )
            rows = await cur.fetchall()

    return {"total": total, "page": page, "size": size, "executions": [dict(row) for row in rows]}

