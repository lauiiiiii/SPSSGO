# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException

from backend.database import (
    get_refresh_token,
    get_user_by_id,
    get_user_by_username,
    revoke_refresh_token,
    revoke_user_refresh_tokens,
    store_refresh_token,
    touch_user_last_login,
    update_user,
)
from backend.security_utils import hash_password, hash_refresh_token, make_refresh_token, verify_password

REFRESH_TOKEN_TTL_SECONDS = 30 * 24 * 3600
_AUTH_EXECUTOR = ThreadPoolExecutor(max_workers=8, thread_name_prefix="spssgo-auth")


async def _run_auth_blocking(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_AUTH_EXECUTOR, func, *args)


async def verify_password_async(password: str, password_hash: str) -> bool:
    return await _run_auth_blocking(verify_password, password, password_hash)


async def hash_password_async(password: str) -> str:
    return await _run_auth_blocking(hash_password, password)


async def authenticate_user(username: str, password: str) -> dict | None:
    user = await get_user_by_username(username)
    if not user or not user.get("is_active", 1):
        return None
    if not await verify_password_async(password, user["password_hash"]):
        return None
    await touch_user_last_login(user["id"])
    user["last_login_at"] = time.time()
    return user


async def issue_refresh_token(user_id: int) -> str:
    token = make_refresh_token()
    await store_refresh_token(user_id, hash_refresh_token(token), time.time() + REFRESH_TOKEN_TTL_SECONDS)
    return token


async def consume_refresh_token(raw_token: str) -> dict | None:
    token_row = await get_refresh_token(hash_refresh_token(raw_token))
    if not token_row:
        return None
    if float(token_row.get("expires_at") or 0) <= time.time():
        await revoke_refresh_token(token_row["token_hash"])
        return None
    user = await get_user_by_id(token_row["user_id"])
    if not user or not user.get("is_active", 1):
        return None
    await revoke_refresh_token(token_row["token_hash"])
    return user


async def change_username(user_id: int, username: str):
    await update_user(user_id, username=username)


async def change_password(user_id: int, new_password: str):
    await update_user(user_id, password_hash=await hash_password_async(new_password))
    await revoke_user_refresh_tokens(user_id)


async def change_username_for_user(user: dict, new_username: str):
    next_username = (new_username or "").strip()
    if not next_username or len(next_username) < 2:
        raise HTTPException(400, "用户名至少2个字符")
    existing = await get_user_by_username(next_username)
    if existing and existing["id"] != user["id"]:
        raise HTTPException(400, "用户名已存在")
    await change_username(user["id"], next_username)
    return {"success": True, "username": next_username}
