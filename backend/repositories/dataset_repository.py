# -*- coding: utf-8 -*-
"""数据集版本仓储，只管 datasets / dataset_versions，别塞文件解析逻辑。"""
import time

import aiomysql

import backend.database as db
from backend.repositories.session_repository import get_session, update_session


async def get_dataset(dataset_id: int | None) -> dict | None:
    if not dataset_id:
        return None
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM datasets WHERE id = %s", (dataset_id,))
            row = await cur.fetchone()
    return dict(row) if row else None


async def get_dataset_for_session(session_id: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM datasets WHERE session_id = %s", (session_id,))
            row = await cur.fetchone()
    return dict(row) if row else None


async def update_dataset(dataset_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k} = %s" for k in kwargs)
    vals = list(kwargs.values()) + [dataset_id]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE datasets SET {sets} WHERE id = %s", vals)


async def upsert_dataset_for_session(
    session_id: str,
    owner_id: int,
    original_filename: str,
    storage_key: str,
    *,
    content_type: str = "",
    size_bytes: int = 0,
):
    existing = await get_dataset_for_session(session_id)
    if existing:
        await update_dataset(
            existing["id"],
            original_filename=original_filename,
            storage_key=storage_key,
            content_type=content_type,
            size_bytes=size_bytes,
        )
        await update_session(session_id, current_dataset_id=existing["id"])
        return await get_dataset(existing["id"])

    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO datasets
                    (owner_id, session_id, original_filename, storage_key, content_type, size_bytes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (owner_id, session_id, original_filename, storage_key, content_type, size_bytes, time.time()),
            )
            dataset_id = cur.lastrowid
    await update_session(session_id, current_dataset_id=dataset_id)
    return await get_dataset(dataset_id)


async def get_dataset_version(version_id: int | None) -> dict | None:
    if not version_id:
        return None
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM dataset_versions WHERE id = %s", (version_id,))
            row = await cur.fetchone()
    if not row:
        return None
    item = dict(row)
    item["summary"] = db._parse_json(item.pop("summary_json", None), {})
    item["preview_rows"] = db._parse_json(item.pop("preview_json", None), [])
    item["schema"] = db._parse_json(item.pop("schema_json", None), {})
    return item


async def get_current_dataset_version_for_session(session_id: str) -> dict | None:
    session = await get_session(session_id)
    if not session:
        return None
    return await get_dataset_version(session.get("current_dataset_version_id"))


async def list_dataset_versions(dataset_id: int) -> list[dict]:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM dataset_versions WHERE dataset_id = %s ORDER BY version_no DESC",
                (dataset_id,),
            )
            rows = await cur.fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["summary"] = db._parse_json(item.pop("summary_json", None), {})
        item["preview_rows"] = db._parse_json(item.pop("preview_json", None), [])
        item["schema"] = db._parse_json(item.pop("schema_json", None), {})
        items.append(item)
    return items


async def create_dataset_version(
    dataset_id: int,
    owner_id: int,
    session_id: str,
    storage_key: str,
    *,
    source_job_id: str | None = None,
    status: str = "ready",
    summary: dict | None = None,
    preview_rows: list | None = None,
    schema: dict | list | None = None,
):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT COALESCE(MAX(version_no), 0) + 1 FROM dataset_versions WHERE dataset_id = %s",
                (dataset_id,),
            )
            version_no = (await cur.fetchone())[0]
            await cur.execute(
                """
                INSERT INTO dataset_versions
                    (dataset_id, owner_id, session_id, version_no, source_job_id, storage_key, status, summary_json, preview_json, schema_json, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    dataset_id,
                    owner_id,
                    session_id,
                    version_no,
                    source_job_id,
                    storage_key,
                    status,
                    db._json_dumps(summary),
                    db._json_dumps(preview_rows),
                    db._json_dumps(schema),
                    time.time(),
                ),
            )
            version_id = cur.lastrowid
    await update_dataset(dataset_id, current_version_id=version_id)
    await update_session(
        session_id,
        current_dataset_id=dataset_id,
        current_dataset_version_id=version_id,
        data_summary=db._json_dumps(summary) if summary is not None else None,
    )
    return await get_dataset_version(version_id)
