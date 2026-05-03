# -*- coding: utf-8 -*-
"""会话服务层，负责路由入参与会话仓储之间的薄编排，别把分析流程塞进来。"""
import json

from fastapi import HTTPException

from backend.database import create_session, delete_session, get_recent_sessions, update_session
from backend.services.session_access import get_session_or_404, is_admin_user


async def create_session_for_user(user: dict) -> dict:
    return {"session_id": await create_session(user["id"])}


async def get_session_info_for_user(session_id: str, user: dict) -> dict:
    session = await get_session_or_404(session_id, user)
    data = dict(session)
    if data.get("data_summary"):
        data["data_summary"] = json.loads(data["data_summary"])
    return data


async def list_sessions_for_user(user: dict) -> dict:
    sessions = await get_recent_sessions(user["id"], is_admin=is_admin_user(user))
    return {"sessions": sessions}


async def rename_session_for_user(session_id: str, title: str, user: dict) -> dict:
    await get_session_or_404(session_id, user)
    next_title = (title or "").strip()
    if not next_title:
        raise HTTPException(400, "标题不能为空")
    await update_session(session_id, research_topic=next_title)
    return {"ok": True}


async def delete_session_for_user(session_id: str, user: dict) -> dict:
    await get_session_or_404(session_id, user)
    await delete_session(session_id)
    return {"ok": True}
