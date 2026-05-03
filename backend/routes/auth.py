# -*- coding: utf-8 -*-
"""认证 API 入口，只接请求和返回协议字段，别把账号校验细节塞进来。"""
from fastapi import APIRouter, Depends, HTTPException, Request

from backend.admin_auth import auth, current_user_required
from backend.config import LOGIN_RATE_LIMIT_COUNT, LOGIN_RATE_LIMIT_WINDOW_SECONDS
from backend.runtime_control import client_ip, enforce_rate_limit
from backend.services.auth_service import (
    authenticate_user,
    change_password as change_password_for_user,
    change_username_for_user,
    consume_refresh_token,
    issue_refresh_token,
    verify_password_async,
)

router = APIRouter()


@router.post("/api/login")
async def login(body: dict, request: Request):
    username = body.get("username", "")
    password = body.get("password", "")
    await enforce_rate_limit(
        "login",
        f"{client_ip(request)}:{username.lower() or 'unknown'}",
        limit=LOGIN_RATE_LIMIT_COUNT,
        window_seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS,
        message="登录尝试过于频繁，请稍后重试",
    )
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    token = auth.create_access_token(uid=str(user["id"]))
    refresh_token = await issue_refresh_token(user["id"])
    return {
        "token": token,
        "access_token": token,
        "refresh_token": refresh_token,
        "username": user["username"],
        "role": user["role"],
        "user_id": user["id"],
    }


@router.post("/api/refresh")
async def refresh_access_token(body: dict):
    refresh_token = body.get("refresh_token", "")
    if not refresh_token:
        raise HTTPException(400, "缺少 refresh_token")
    user = await consume_refresh_token(refresh_token)
    if not user:
        raise HTTPException(401, "刷新令牌无效或已过期")
    token = auth.create_access_token(uid=str(user["id"]))
    next_refresh_token = await issue_refresh_token(user["id"])
    return {
        "token": token,
        "access_token": token,
        "refresh_token": next_refresh_token,
        "username": user["username"],
        "role": user["role"],
        "user_id": user["id"],
    }


@router.get("/api/me")
async def get_current_user(user=Depends(current_user_required)):
    return {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
    }


@router.post("/api/change-username")
async def change_username(body: dict, user=Depends(current_user_required)):
    return await change_username_for_user(user, body.get("new_username", ""))


@router.post("/api/change-password")
async def change_password(body: dict, user=Depends(current_user_required)):
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")
    if not old_password or not new_password:
        raise HTTPException(400, "请填写完整")
    if len(new_password) < 6:
        raise HTTPException(400, "新密码至少6位")
    if not await verify_password_async(old_password, user["password_hash"]):
        raise HTTPException(400, "当前密码错误")
    await change_password_for_user(user["id"], new_password)
    return {"success": True}

