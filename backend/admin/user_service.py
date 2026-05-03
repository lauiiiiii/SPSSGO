# -*- coding: utf-8 -*-
"""管理员账号服务，只管后台用户管理规则，别把表单和 SQL 细节揉进来。"""
from __future__ import annotations

from fastapi import HTTPException

from backend.admin.user_repository import count_active_admin_users, list_admin_users
from backend.repositories.user_repository import create_user, get_user_by_id, get_user_by_username, revoke_user_refresh_tokens, update_user
from backend.services.auth_service import hash_password_async

VALID_USER_ROLES = {"user", "admin"}


def _normalize_role(role: str | None) -> str:
    value = (role or "user").strip().lower()
    if value not in VALID_USER_ROLES:
        raise HTTPException(400, "用户角色不支持")
    return value


def _normalize_username(username: str | None) -> str:
    value = (username or "").strip()
    if len(value) < 2:
        raise HTTPException(400, "用户名至少2个字符")
    return value


def _normalize_password(password: str | None) -> str:
    value = str(password or "")
    if len(value) < 6:
        raise HTTPException(400, "密码至少6位")
    return value


async def get_admin_users(page: int, size: int, *, keyword: str = "", role: str = "", is_active: str = "") -> dict:
    active_filter = None
    if is_active != "":
        if str(is_active) not in {"0", "1"}:
            raise HTTPException(400, "账号状态参数无效")
        active_filter = int(is_active)
    normalized_role = ""
    if role:
        normalized_role = _normalize_role(role)
    safe_page = max(1, int(page or 1))
    safe_size = min(100, max(1, int(size or 20)))
    return await list_admin_users(
        safe_page,
        safe_size,
        keyword=(keyword or "").strip(),
        role=normalized_role,
        is_active=active_filter,
    )


async def create_admin_user(payload: dict) -> dict:
    username = _normalize_username(payload.get("username"))
    password = _normalize_password(payload.get("password"))
    role = _normalize_role(payload.get("role"))
    existing = await get_user_by_username(username)
    if existing:
        raise HTTPException(400, "用户名已存在")
    user_id = await create_user(username, password, role=role)
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(500, "用户创建失败")
    return _serialize_user(user)


async def update_admin_user(target_user_id: int, payload: dict, acting_user: dict) -> dict:
    target = await get_user_by_id(target_user_id)
    if not target:
        raise HTTPException(404, "用户不存在")

    updates = {}
    if "username" in payload:
        username = _normalize_username(payload.get("username"))
        existing = await get_user_by_username(username)
        if existing and existing["id"] != target_user_id:
            raise HTTPException(400, "用户名已存在")
        updates["username"] = username

    if "role" in payload:
        next_role = _normalize_role(payload.get("role"))
        if target["role"] == "admin" and next_role != "admin":
            await _ensure_not_last_admin(target, acting_user)
        updates["role"] = next_role

    if not updates:
        raise HTTPException(400, "没有可更新的字段")

    await update_user(target_user_id, **updates)
    user = await get_user_by_id(target_user_id)
    if not user:
        raise HTTPException(500, "用户更新失败")
    return _serialize_user(user)


async def reset_admin_user_password(target_user_id: int, new_password: str) -> dict:
    target = await get_user_by_id(target_user_id)
    if not target:
        raise HTTPException(404, "用户不存在")
    password = _normalize_password(new_password)
    await update_user(target_user_id, password_hash=await hash_password_async(password))
    await revoke_user_refresh_tokens(target_user_id)
    return {"success": True}


async def toggle_admin_user_active(target_user_id: int, is_active: bool, acting_user: dict) -> dict:
    target = await get_user_by_id(target_user_id)
    if not target:
        raise HTTPException(404, "用户不存在")
    next_active = 1 if bool(is_active) else 0
    if target["id"] == acting_user["id"] and not next_active:
        raise HTTPException(400, "不能停用当前登录账号")
    if target["role"] == "admin" and not next_active:
        await _ensure_not_last_admin(target, acting_user)
    await update_user(target_user_id, is_active=next_active)
    if not next_active:
        await revoke_user_refresh_tokens(target_user_id)
    user = await get_user_by_id(target_user_id)
    if not user:
        raise HTTPException(500, "用户状态更新失败")
    return _serialize_user(user)


async def _ensure_not_last_admin(target: dict, acting_user: dict) -> None:
    if target["role"] != "admin":
        return
    if target["id"] == acting_user["id"]:
        raise HTTPException(400, "不能修改当前登录管理员的关键权限")
    remaining = await count_active_admin_users(exclude_user_id=target["id"])
    if remaining < 1:
        raise HTTPException(400, "系统至少需要保留一个启用中的管理员")


def _serialize_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "is_active": int(user.get("is_active", 1)),
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
    }
