# -*- coding: utf-8 -*-
"""沙箱执行仓储，只管 sandbox_executions 表，别把容器调度细节塞进来。"""
import time
import uuid

import aiomysql

import backend.database as db


async def create_sandbox_execution(
    job_id: str,
    owner_id: int,
    *,
    session_id: str | None = None,
    dataset_version_id: int | None = None,
    celery_task_id: str | None = None,
    queue: str = "sandbox",
    status: str = "queued",
    executor_mode: str | None = None,
    docker_image: str | None = None,
    container_name: str | None = None,
    data_storage_key: str | None = None,
    error_message: str | None = None,
    details: dict | list | None = None,
    started_at: float | None = None,
):
    execution_id = uuid.uuid4().hex[:12]
    created_at = time.time()
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO sandbox_executions
                    (
                        execution_id, job_id, owner_id, session_id, dataset_version_id,
                        celery_task_id, queue_name, status, executor_mode, docker_image,
                        container_name, data_storage_key, created_at, started_at,
                        error_message, details_json
                    )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    execution_id,
                    job_id,
                    owner_id,
                    session_id,
                    dataset_version_id,
                    celery_task_id,
                    queue,
                    status,
                    executor_mode,
                    docker_image,
                    container_name,
                    data_storage_key,
                    created_at,
                    started_at,
                    error_message,
                    db._json_dumps(details),
                ),
            )
    return await get_sandbox_execution(execution_id)


async def get_sandbox_execution(execution_id: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM sandbox_executions WHERE execution_id = %s",
                (execution_id,),
            )
            row = await cur.fetchone()
    return db._normalize_sandbox_execution_row(row)


async def update_sandbox_execution(execution_id: str, **kwargs):
    if not kwargs:
        return
    normalized = {}
    for key, value in kwargs.items():
        if key == "details":
            normalized["details_json"] = db._json_dumps(value)
        elif key == "queue":
            normalized["queue_name"] = value
        else:
            normalized[key] = value

    if "finished_at" in normalized:
        finished_at = normalized.get("finished_at")
        started_at = normalized.get("started_at")
        if started_at is None:
            current = await get_sandbox_execution(execution_id)
            started_at = (current or {}).get("started_at")
        if finished_at is not None and started_at is not None and "duration_ms" not in normalized:
            normalized["duration_ms"] = max(0, int((finished_at - started_at) * 1000))

    sets = ", ".join(f"{k} = %s" for k in normalized)
    vals = list(normalized.values()) + [execution_id]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE sandbox_executions SET {sets} WHERE execution_id = %s", vals)


async def list_sandbox_executions_for_job(job_id: str) -> list[dict]:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM sandbox_executions WHERE job_id = %s ORDER BY id DESC",
                (job_id,),
            )
            rows = await cur.fetchall()
    return [db._normalize_sandbox_execution_row(row) for row in rows]


async def cancel_active_sandbox_executions_for_job(job_id: str, error_message: str = "父任务已取消"):
    now = time.time()
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE sandbox_executions
                SET status = %s,
                    error_message = %s,
                    finished_at = COALESCE(finished_at, %s),
                    duration_ms = CASE
                        WHEN started_at IS NULL THEN duration_ms
                        ELSE COALESCE(duration_ms, GREATEST(0, CAST((%s - started_at) * 1000 AS SIGNED)))
                    END
                WHERE job_id = %s AND status IN ('queued', 'running')
                """,
                ("canceled", error_message, now, now, job_id),
            )
