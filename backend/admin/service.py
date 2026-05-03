# -*- coding: utf-8 -*-
"""管理后台业务编排层，别把 SQL 和前端表单细节塞进来。"""
from fastapi import HTTPException

from backend.config import (
    JOB_BACKEND,
    MAX_CONCURRENT_TASKS,
    MAX_EXECUTION_SECONDS,
    MAX_UPLOAD_SIZE_MB,
    SESSION_EXPIRE_HOURS,
)
from backend.database import cleanup_expired, get_session
from backend.admin.repository import delete_session_records, get_dashboard_stats, list_admin_sessions
from backend.admin.repository import (
    get_admin_operations_summary,
    list_admin_jobs,
    list_admin_sandbox_executions,
)
from backend.admin.user_service import (
    create_admin_user as create_admin_user_record,
    get_admin_users as get_admin_users_page,
    reset_admin_user_password as reset_admin_user_password_record,
    toggle_admin_user_active as toggle_admin_user_active_record,
    update_admin_user as update_admin_user_record,
)
from backend.services.ai_settings_service import get_ai_config_for_admin, get_ai_runtime_config, save_ai_config_for_admin
from backend.storage import storage_service


async def get_admin_dashboard():
    stats = await get_dashboard_stats()
    stats["storage"] = {
        "uploads_mb": round(storage_service.category_size("uploads") / 1024 / 1024, 1),
        "outputs_mb": round(storage_service.category_size("outputs") / 1024 / 1024, 1),
    }
    return stats


async def get_admin_sessions(page: int, size: int):
    return await list_admin_sessions(page, size)


async def get_admin_users(page: int, size: int, *, keyword: str = "", role: str = "", is_active: str = ""):
    return await get_admin_users_page(page, size, keyword=keyword, role=role, is_active=is_active)


async def create_admin_user(payload: dict):
    return await create_admin_user_record(payload)


async def update_admin_user(user_id: int, payload: dict, acting_user: dict):
    return await update_admin_user_record(user_id, payload, acting_user)


async def reset_admin_user_password(user_id: int, new_password: str):
    return await reset_admin_user_password_record(user_id, new_password)


async def toggle_admin_user_active(user_id: int, is_active: bool, acting_user: dict):
    return await toggle_admin_user_active_record(user_id, is_active, acting_user)


async def delete_admin_session(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    storage_service.delete_session(session_id)
    await delete_session_records(session_id)
    return {"ok": True}


async def cleanup_admin_sessions():
    await cleanup_expired()
    return {"ok": True, "message": "过期会话已清理"}


async def get_admin_operations():
    return await get_admin_operations_summary()


async def get_admin_jobs(page: int, size: int, status: str = "", queue: str = "", job_type: str = ""):
    return await list_admin_jobs(page, size, status=status, queue=queue, job_type=job_type)


async def get_admin_sandbox_executions(page: int, size: int, status: str = "", executor_mode: str = ""):
    return await list_admin_sandbox_executions(page, size, status=status, executor_mode=executor_mode)


async def get_admin_ai_config():
    return await get_ai_config_for_admin()


async def save_admin_ai_config(payload: dict):
    return await save_ai_config_for_admin(payload)


async def get_admin_system_info():
    import platform
    ai_config = await get_ai_runtime_config()
    return {
        "python_version": platform.python_version(),
        "system": f"{platform.system()} {platform.release()}",
        "ai_provider": ai_config["provider"],
        "ai_model": ai_config["model"],
        "ai_base_url": ai_config["base_url"],
        "ai_has_api_key": bool(ai_config["api_key"]),
        "job_backend": JOB_BACKEND,
        "max_upload_mb": MAX_UPLOAD_SIZE_MB,
        "max_exec_seconds": MAX_EXECUTION_SECONDS,
        "session_expire_hours": SESSION_EXPIRE_HOURS,
        "max_concurrent_tasks": MAX_CONCURRENT_TASKS,
    }

