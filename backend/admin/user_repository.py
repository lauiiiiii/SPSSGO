# -*- coding: utf-8 -*-
"""管理员用户仓储，只放后台账号管理查询，别塞登录流程和路由判断。"""
from __future__ import annotations

import aiomysql

import backend.database as db


def _build_filter_clause(filters: list[tuple[str, object]]):
    if not filters:
        return "", []
    return " WHERE " + " AND ".join(item[0] for item in filters), [item[1] for item in filters]


async def list_admin_users(
    page: int,
    size: int,
    *,
    keyword: str = "",
    role: str = "",
    is_active: int | None = None,
) -> dict:
    offset = (page - 1) * size
    filters: list[tuple[str, object]] = []
    if keyword:
        filters.append(("u.username LIKE %s", f"%{keyword}%"))
    if role:
        filters.append(("u.role = %s", role))
    if is_active is not None:
        filters.append(("u.is_active = %s", is_active))
    where_clause, where_params = _build_filter_clause(filters)

    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT COUNT(*) FROM users u{where_clause}", where_params)
            total = (await cur.fetchone())[0]

        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                f"""
                SELECT
                    u.id,
                    u.username,
                    u.role,
                    u.is_active,
                    u.created_at,
                    u.last_login_at,
                    COUNT(rt.id) AS active_refresh_tokens
                FROM users u
                LEFT JOIN refresh_tokens rt
                    ON rt.user_id = u.id AND rt.revoked_at IS NULL AND rt.expires_at > UNIX_TIMESTAMP()
                {where_clause}
                GROUP BY u.id
                ORDER BY u.created_at DESC, u.id DESC
                LIMIT %s OFFSET %s
                """,
                where_params + [size, offset],
            )
            rows = await cur.fetchall()

    return {
        "total": total,
        "page": page,
        "size": size,
        "users": [dict(row) for row in rows],
    }


async def count_active_admin_users(*, exclude_user_id: int | None = None) -> int:
    sql = "SELECT COUNT(*) FROM users WHERE role = %s AND is_active = 1"
    params: list[object] = ["admin"]
    if exclude_user_id is not None:
        sql += " AND id <> %s"
        params.append(exclude_user_id)
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return (await cur.fetchone())[0]
