# -*- coding: utf-8 -*-
"""Shared session access helpers for route and service layers."""

from fastapi import HTTPException

from backend.database import get_session_for_user


def is_admin_user(user: dict | None) -> bool:
    return bool(user and user.get("role") == "admin")


async def get_session_or_404(session_id: str, user: dict):
    session = await get_session_for_user(
        session_id,
        user["id"],
        is_admin=is_admin_user(user),
    )
    if not session:
        raise HTTPException(404, "会话不存在")
    return session
