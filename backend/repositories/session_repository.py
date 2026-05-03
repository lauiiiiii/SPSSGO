# -*- coding: utf-8 -*-
"""会话仓储，只管 sessions 生命周期，别塞分析和文件处理逻辑。"""
import time
import uuid

import aiomysql

import backend.database as db
from backend.config import SESSION_EXPIRE_HOURS
from backend.domain import CREATED
from backend.storage import storage_service


async def create_session(owner_id: int | None = None) -> str:
    session_id = uuid.uuid4().hex[:12]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO sessions (id, owner_id, created_at, status) VALUES (%s, %s, %s, %s)",
                (session_id, owner_id, time.time(), CREATED),
            )
    storage_service.ensure_session(session_id)
    return session_id


async def get_session(session_id: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
            row = await cur.fetchone()
    return dict(row) if row else None


async def get_session_for_user(session_id: str, owner_id: int, *, is_admin: bool = False) -> dict | None:
    if is_admin:
        return await get_session(session_id)
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM sessions WHERE id = %s AND owner_id = %s",
                (session_id, owner_id),
            )
            row = await cur.fetchone()
    return dict(row) if row else None


async def update_session(session_id: str, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k} = %s" for k in kwargs)
    vals = list(kwargs.values()) + [session_id]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE sessions SET {sets} WHERE id = %s", vals)


async def get_recent_sessions(owner_id: int | None = None, *, is_admin: bool = False, limit: int = 50) -> list[dict]:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            sql = (
                "SELECT id, owner_id, created_at, research_topic, status "
                "FROM sessions"
            )
            params = []
            if owner_id is not None and not is_admin:
                sql += " WHERE owner_id = %s"
                params.append(owner_id)
            sql += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            await cur.execute(sql, params)
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def cleanup_expired():
    cutoff = time.time() - SESSION_EXPIRE_HOURS * 3600
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "DELETE FROM refresh_tokens WHERE expires_at < %s OR revoked_at IS NOT NULL",
                (time.time(),),
            )
            await cur.execute("SELECT id FROM sessions WHERE created_at < %s", (cutoff,))
            expired = await cur.fetchall()
            for row in expired:
                sid = row["id"]
                storage_service.delete_session(sid)
            await cur.execute("DELETE FROM sessions WHERE created_at < %s", (cutoff,))


async def delete_session(session_id: str):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
