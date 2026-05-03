# -*- coding: utf-8 -*-
"""统一认证模块：基于 AuthX 的 JWT 认证，前后台共用"""
from fastapi import Depends, FastAPI, HTTPException
from authx import AuthX, AuthXConfig
from backend.config import ADMIN_SECRET_KEY
from backend.database import get_user_by_id

config = AuthXConfig(
    JWT_SECRET_KEY=ADMIN_SECRET_KEY,
    JWT_TOKEN_LOCATION=["headers"],
    JWT_ACCESS_TOKEN_EXPIRES=86400,  # 24h
)

auth = AuthX(config=config)


def setup_auth(app: FastAPI):
    auth.handle_errors(app)


async def current_user_required(payload=Depends(auth.access_token_required)):
    try:
        user_id = int(payload.sub)
    except Exception as exc:
        raise HTTPException(401, "无效的身份令牌") from exc
    user = await get_user_by_id(user_id)
    if not user or not user.get("is_active", 1):
        raise HTTPException(401, "用户不存在或已被禁用")
    return user


async def admin_required(user=Depends(current_user_required)):
    if user.get("role") != "admin":
        raise HTTPException(403, "需要管理员权限")
    return user

