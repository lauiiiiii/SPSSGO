# -*- coding: utf-8 -*-
"""会话 API 入口，只接参数和转发，别把仓储细节塞进来。"""
from fastapi import APIRouter, Depends, Form

from backend.admin_auth import current_user_required
from backend.services.session_service import (
    create_session_for_user,
    delete_session_for_user,
    get_session_info_for_user,
    list_sessions_for_user,
    rename_session_for_user,
)

router = APIRouter()


@router.post("/api/session")
async def new_session(user=Depends(current_user_required)):
    return await create_session_for_user(user)


@router.get("/api/session/{session_id}")
async def get_session_info(session_id: str, user=Depends(current_user_required)):
    return await get_session_info_for_user(session_id, user)


@router.get("/api/sessions")
async def list_sessions(user=Depends(current_user_required)):
    return await list_sessions_for_user(user)


@router.patch("/api/session/{session_id}/title")
async def rename_session(session_id: str, title: str = Form(...), user=Depends(current_user_required)):
    return await rename_session_for_user(session_id, title, user)


@router.delete("/api/session/{session_id}")
async def remove_session(session_id: str, user=Depends(current_user_required)):
    return await delete_session_for_user(session_id, user)

