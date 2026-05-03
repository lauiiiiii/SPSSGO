# -*- coding: utf-8 -*-
"""任务仓储，只管 jobs 表，别把调度和业务状态机塞进来。"""
import time
import uuid

import aiomysql

import backend.database as db
from backend.domain import PENDING


async def create_job(
    job_type: str,
    owner_id: int,
    queue: str,
    *,
    session_id: str | None = None,
    dataset_id: int | None = None,
    dataset_version_id: int | None = None,
    payload: dict | None = None,
    status: str = PENDING,
):
    job_id = uuid.uuid4().hex[:12]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO jobs
                    (id, job_type, owner_id, session_id, dataset_id, dataset_version_id, status, queue_name, payload_json, progress_json, result_json, attempts, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    job_id,
                    job_type,
                    owner_id,
                    session_id,
                    dataset_id,
                    dataset_version_id,
                    status,
                    queue,
                    db._json_dumps(payload or {}),
                    db._json_dumps({}),
                    db._json_dumps({}),
                    0,
                    time.time(),
                ),
            )
    return await get_job(job_id)


async def get_job(job_id: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
            row = await cur.fetchone()
    return db._normalize_job_row(row)


async def get_job_for_user(job_id: str, owner_id: int, *, is_admin: bool = False) -> dict | None:
    if is_admin:
        return await get_job(job_id)
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM jobs WHERE id = %s AND owner_id = %s",
                (job_id, owner_id),
            )
            row = await cur.fetchone()
    return db._normalize_job_row(row)


async def update_job(job_id: str, **kwargs):
    if not kwargs:
        return
    normalized = {}
    for key, value in kwargs.items():
        if key in {"payload", "progress", "result"}:
            normalized[f"{key}_json"] = db._json_dumps(value)
        elif key == "queue":
            normalized["queue_name"] = value
        else:
            normalized[key] = value
    sets = ", ".join(f"{k} = %s" for k in normalized)
    vals = list(normalized.values()) + [job_id]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE jobs SET {sets} WHERE id = %s", vals)


async def list_jobs_for_session(
    session_id: str,
    owner_id: int | None = None,
    *,
    is_admin: bool = False,
    statuses: list[str] | tuple[str, ...] | None = None,
    limit: int = 20,
) -> list[dict]:
    sql = "SELECT * FROM jobs WHERE session_id = %s"
    params = [session_id]
    if owner_id is not None and not is_admin:
        sql += " AND owner_id = %s"
        params.append(owner_id)
    if statuses:
        placeholders = ",".join(["%s"] * len(statuses))
        sql += f" AND status IN ({placeholders})"
        params.extend(list(statuses))
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, params)
            rows = await cur.fetchall()
    return [db._normalize_job_row(row) for row in rows]
