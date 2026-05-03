# -*- coding: utf-8 -*-
"""管理后台 API 入口，只做参数接收和服务转发，别写业务编排。"""
from pydantic import BaseModel
from fastapi import APIRouter, Depends

from backend.admin_auth import current_user_required

from backend.admin.service import (
    cleanup_admin_sessions,
    create_admin_user,
    delete_admin_session,
    get_admin_ai_config,
    get_admin_dashboard,
    get_admin_jobs,
    get_admin_operations,
    get_admin_sessions,
    get_admin_sandbox_executions,
    get_admin_system_info,
    get_admin_users,
    save_admin_ai_config,
    toggle_admin_user_active,
    update_admin_user,
    reset_admin_user_password,
)

router = APIRouter()


class AdminAIConfigPayload(BaseModel):
    provider: str = "deepseek"
    base_url: str = ""
    model: str = ""
    api_key: str = ""
    clear_api_key: bool = False


class AdminUserCreatePayload(BaseModel):
    username: str
    password: str
    role: str = "user"


class AdminUserUpdatePayload(BaseModel):
    username: str = ""
    role: str = ""


class AdminUserResetPasswordPayload(BaseModel):
    new_password: str


class AdminUserToggleActivePayload(BaseModel):
    is_active: bool


@router.get("/api/admin/dashboard")
async def admin_dashboard():
    return await get_admin_dashboard()


@router.get("/api/admin/users")
async def admin_list_users(page: int = 1, size: int = 20, keyword: str = "", role: str = "", is_active: str = ""):
    return await get_admin_users(page, size, keyword=keyword, role=role, is_active=is_active)


@router.post("/api/admin/users")
async def admin_create_user(payload: AdminUserCreatePayload):
    return await create_admin_user(payload.dict())


@router.put("/api/admin/users/{user_id}")
async def admin_update_user(user_id: int, payload: AdminUserUpdatePayload, user=Depends(current_user_required)):
    return await update_admin_user(user_id, payload.dict(exclude_unset=True), user)


@router.post("/api/admin/users/{user_id}/reset-password")
async def admin_reset_user_password(user_id: int, payload: AdminUserResetPasswordPayload):
    return await reset_admin_user_password(user_id, payload.new_password)


@router.post("/api/admin/users/{user_id}/toggle-active")
async def admin_toggle_user_active(
    user_id: int,
    payload: AdminUserToggleActivePayload,
    user=Depends(current_user_required),
):
    return await toggle_admin_user_active(user_id, payload.is_active, user)


@router.get("/api/admin/sessions")
async def admin_list_sessions(page: int = 1, size: int = 20):
    return await get_admin_sessions(page, size)


@router.get("/api/admin/operations")
async def admin_operations():
    return await get_admin_operations()


@router.get("/api/admin/jobs")
async def admin_list_jobs(page: int = 1, size: int = 20, status: str = "", queue: str = "", job_type: str = ""):
    return await get_admin_jobs(page, size, status=status, queue=queue, job_type=job_type)


@router.get("/api/admin/sandbox-executions")
async def admin_list_sandbox_executions(page: int = 1, size: int = 20, status: str = "", executor_mode: str = ""):
    return await get_admin_sandbox_executions(page, size, status=status, executor_mode=executor_mode)


@router.delete("/api/admin/sessions/{session_id}")
async def admin_delete_session(session_id: str):
    return await delete_admin_session(session_id)


@router.post("/api/admin/cleanup")
async def admin_cleanup():
    return await cleanup_admin_sessions()


@router.get("/api/admin/system")
async def admin_system_info():
    return await get_admin_system_info()


@router.get("/api/admin/ai-config")
async def admin_ai_config():
    return await get_admin_ai_config()


@router.put("/api/admin/ai-config")
async def admin_save_ai_config(payload: AdminAIConfigPayload):
    return await save_admin_ai_config(payload.dict())

