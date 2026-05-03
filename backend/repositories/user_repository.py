# -*- coding: utf-8 -*-
"""用户和令牌仓储，只管 users / refresh_tokens，别塞登录流程。"""
import time

import aiomysql

import backend.database as db
from backend.config import ADMIN_PASSWORD, ADMIN_USERNAME
from backend.security_utils import hash_password


async def bootstrap_initial_admin():
    existing_admin = await get_user_by_username(ADMIN_USERNAME)
    if existing_admin:
        admin_id = existing_admin["id"]
    else:
        admin_id = await create_user(ADMIN_USERNAME, ADMIN_PASSWORD, role="admin")
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE sessions SET owner_id = %s WHERE owner_id IS NULL",
                (admin_id,),
            )


async def create_user(username: str, password: str, role: str = "user") -> int:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (%s, %s, %s, %s)",
                (username, hash_password(password), role, time.time()),
            )
            return cur.lastrowid


async def get_user_by_id(user_id: int) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = await cur.fetchone()
    return dict(row) if row else None


async def get_user_by_username(username: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = await cur.fetchone()
    return dict(row) if row else None


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k} = %s" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE users SET {sets} WHERE id = %s", vals)


async def touch_user_last_login(user_id: int):
    await update_user(user_id, last_login_at=time.time())


async def store_refresh_token(user_id: int, token_hash: str, expires_at: float):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO refresh_tokens (user_id, token_hash, expires_at, created_at) VALUES (%s, %s, %s, %s)",
                (user_id, token_hash, expires_at, time.time()),
            )


async def get_refresh_token(token_hash: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM refresh_tokens WHERE token_hash = %s AND revoked_at IS NULL",
                (token_hash,),
            )
            row = await cur.fetchone()
    return dict(row) if row else None


async def revoke_refresh_token(token_hash: str):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE refresh_tokens SET revoked_at = %s WHERE token_hash = %s AND revoked_at IS NULL",
                (time.time(), token_hash),
            )


async def revoke_user_refresh_tokens(user_id: int):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE refresh_tokens SET revoked_at = %s WHERE user_id = %s AND revoked_at IS NULL",
                (time.time(), user_id),
            )
