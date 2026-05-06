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


DATASET_SORT_SQL = {
    "recent": "COALESCE(d.last_used_at, d.created_at) DESC, d.created_at DESC",
    "created": "d.created_at DESC",
    "name": "COALESCE(NULLIF(d.name, ''), NULLIF(s.research_topic, ''), d.original_filename) ASC, d.created_at DESC",
    "versions": "COALESCE(vc.version_count, 0) DESC, d.created_at DESC",
    "results": "COALESCE(rc.result_count, 0) DESC, d.created_at DESC",
}


def _dataset_where(owner_id: int | None, is_admin: bool, query: str | None, in_folder: int | None = None) -> tuple[str, list]:
    clauses = []
    params = []
    if owner_id is not None and not is_admin:
        clauses.append("d.owner_id = %s")
        params.append(owner_id)
    keyword = (query or "").strip()
    if keyword:
        like = f"%{keyword}%"
        clauses.append(
            """
            (
                d.name LIKE %s
                OR d.original_filename LIKE %s
                OR s.research_topic LIKE %s
                OR d.session_id LIKE %s
            )
            """
        )
        params.extend([like, like, like, like])
    if in_folder == 0:
        clauses.append("fi.folder_id IS NULL")
    elif in_folder == 1:
        clauses.append("fi.folder_id IS NOT NULL")
    if not clauses:
        return "", params
    return "WHERE " + " AND ".join(clauses), params


async def count_datasets_for_owner(
    owner_id: int | None = None,
    *,
    is_admin: bool = False,
    query: str | None = None,
    in_folder: int | None = None,
) -> int:
    where_clause, params = _dataset_where(owner_id, is_admin, query, in_folder)
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT COUNT(*)
                FROM datasets d
                LEFT JOIN sessions s ON s.id = d.session_id
                LEFT JOIN dataset_folder_items fi ON fi.dataset_id = d.id
                {where_clause}
                """,
                params,
            )
            row = await cur.fetchone()
    return int(row[0] if row else 0)


async def list_datasets_for_owner(
    owner_id: int | None = None,
    *,
    is_admin: bool = False,
    limit: int = 200,
    offset: int = 0,
    query: str | None = None,
    sort: str = "recent",
    in_folder: int | None = None,
) -> list[dict]:
    params = []
    where_clause, params = _dataset_where(owner_id, is_admin, query, in_folder)
    order_sql = DATASET_SORT_SQL.get(sort, DATASET_SORT_SQL["recent"])

    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"""
                SELECT
                    d.*,
                    s.research_topic,
                    s.status AS session_status,
                    s.current_dataset_version_id,
                    dv.version_no AS current_version_no,
                    dv.summary_json AS current_summary_json,
                    COALESCE(vc.version_count, 0) AS version_count,
                    COALESCE(rc.result_count, 0) AS result_count,
                    fi.folder_id
                FROM datasets d
                LEFT JOIN sessions s ON s.id = d.session_id
                LEFT JOIN dataset_versions dv ON dv.id = d.current_version_id
                LEFT JOIN dataset_folder_items fi ON fi.dataset_id = d.id
                LEFT JOIN (
                    SELECT dataset_id, COUNT(*) AS version_count
                    FROM dataset_versions
                    GROUP BY dataset_id
                ) vc ON vc.dataset_id = d.id
                LEFT JOIN (
                    SELECT session_id, COUNT(*) AS result_count
                    FROM results
                    GROUP BY session_id
                ) rc ON rc.session_id = d.session_id
                {where_clause}
                ORDER BY {order_sql}
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = await cur.fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["current_summary"] = db._parse_json(item.pop("current_summary_json", None), {})
        item["folder_id"] = item.get("folder_id")
        items.append(item)
    return items


async def update_dataset(dataset_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k} = %s" for k in kwargs)
    vals = list(kwargs.values()) + [dataset_id]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE datasets SET {sets} WHERE id = %s", vals)


async def touch_dataset(dataset_id: int) -> None:
    await update_dataset(dataset_id, last_used_at=time.time())


async def update_dataset_version(version_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k} = %s" for k in kwargs)
    vals = list(kwargs.values()) + [version_id]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE dataset_versions SET {sets} WHERE id = %s", vals)


async def delete_dataset_version(version_id: int) -> dict:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM results WHERE dataset_version_id = %s", (version_id,))
            deleted_results = cur.rowcount
            await cur.execute("DELETE FROM dataset_versions WHERE id = %s", (version_id,))
            deleted_versions = cur.rowcount
    return {"deleted_versions": deleted_versions, "deleted_results": deleted_results}


async def copy_dataset_version(version_id: int, name: str | None = None) -> dict | None:
    source = await get_dataset_version(version_id)
    if not source:
        return None
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT COALESCE(MAX(version_no), 0) + 1 FROM dataset_versions WHERE dataset_id = %s",
                (source["dataset_id"],),
            )
            version_no = (await cur.fetchone())[0]
            await cur.execute(
                """
                INSERT INTO dataset_versions
                    (dataset_id, owner_id, session_id, version_no, name, source_job_id, storage_key, status, summary_json, preview_json, schema_json, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    source["dataset_id"],
                    source["owner_id"],
                    source["session_id"],
                    version_no,
                    name,
                    source.get("source_job_id"),
                    source["storage_key"],
                    source.get("status") or "ready",
                    db._json_dumps(source.get("summary")),
                    db._json_dumps(source.get("preview_rows")),
                    db._json_dumps(source.get("schema")),
                    time.time(),
                ),
            )
            next_id = cur.lastrowid
    await update_dataset(source["dataset_id"], current_version_id=next_id, last_used_at=time.time())
    await update_session(
        source["session_id"],
        current_dataset_id=source["dataset_id"],
        current_dataset_version_id=next_id,
        data_summary=db._json_dumps(source.get("summary")),
    )
    return await get_dataset_version(next_id)


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
            last_used_at=time.time(),
        )
        await update_session(session_id, current_dataset_id=existing["id"])
        return await get_dataset(existing["id"])

    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO datasets
                    (owner_id, session_id, name, original_filename, storage_key, content_type, size_bytes, created_at, last_used_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (owner_id, session_id, None, original_filename, storage_key, content_type, size_bytes, time.time(), time.time()),
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
                """
                SELECT
                    dv.*,
                    j.status AS source_job_status,
                    j.job_type AS source_job_type,
                    j.payload_json AS source_job_payload_json
                FROM dataset_versions dv
                LEFT JOIN jobs j ON j.id = dv.source_job_id
                WHERE dv.dataset_id = %s
                ORDER BY dv.version_no DESC
                """,
                (dataset_id,),
            )
            rows = await cur.fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["summary"] = db._parse_json(item.pop("summary_json", None), {})
        item["preview_rows"] = db._parse_json(item.pop("preview_json", None), [])
        item["schema"] = db._parse_json(item.pop("schema_json", None), {})
        source_payload = db._parse_json(item.pop("source_job_payload_json", None), {})
        item["source_method"] = source_payload.get("method") if isinstance(source_payload, dict) else None
        item["source_job_status"] = item.get("source_job_status")
        item["source_job_type"] = item.get("source_job_type")
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
    await update_dataset(dataset_id, current_version_id=version_id, last_used_at=time.time())
    await update_session(
        session_id,
        current_dataset_id=dataset_id,
        current_dataset_version_id=version_id,
        data_summary=db._json_dumps(summary) if summary is not None else None,
    )
    return await get_dataset_version(version_id)
