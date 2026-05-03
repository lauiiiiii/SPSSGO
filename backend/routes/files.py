# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, File, Request, UploadFile

from backend.admin_auth import current_user_required
from backend.config import UPLOAD_RATE_LIMIT_COUNT, UPLOAD_RATE_LIMIT_WINDOW_SECONDS
from backend.runtime_control import client_ip, enforce_rate_limit
from backend.services.job_service import submit_upload_job
from backend.services.session_access import get_session_or_404
from backend.services.session_data_service import allow_legacy_upload_reads
from backend.services.upload_service import (
    build_data_preview_for_session,
    download_data_file_for_session,
    export_data_file_for_session,
    get_questionnaire_content_for_session,
    get_variable_values_for_session,
    get_variables_for_session,
    list_files_for_session,
    upload_file_for_session,
)

router = APIRouter()

@router.post("/api/upload/{session_id}")
async def upload_file(session_id: str, request: Request, file: UploadFile = File(...), user=Depends(current_user_required)):
    await enforce_rate_limit(
        "upload",
        f"user:{user['id']}:{client_ip(request)}",
        limit=UPLOAD_RATE_LIMIT_COUNT,
        window_seconds=UPLOAD_RATE_LIMIT_WINDOW_SECONDS,
        message="上传过于频繁，请稍后重试",
    )
    return await submit_upload_job(session_id, user, file)


@router.get("/api/files/{session_id}")
async def list_files(session_id: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await list_files_for_session(session_id)


@router.get("/api/questionnaire/{session_id}/{filename}")
async def get_questionnaire_content(session_id: str, filename: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await get_questionnaire_content_for_session(session_id, filename)


@router.get("/api/data-preview/{session_id}")
async def data_preview(session_id: str, limit: int = 100, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await build_data_preview_for_session(
        session_id,
        limit,
        allow_legacy_fallback=allow_legacy_upload_reads(user),
    )


@router.get("/api/variable-values/{session_id}/{column_name:path}")
async def get_variable_values(session_id: str, column_name: str, limit: int = 200, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await get_variable_values_for_session(
        session_id,
        column_name,
        limit,
        allow_legacy_fallback=allow_legacy_upload_reads(user),
    )


@router.get("/api/data-file/{session_id}")
async def download_data_file(session_id: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await download_data_file_for_session(
        session_id,
        allow_legacy_fallback=allow_legacy_upload_reads(user),
    )


@router.get("/api/data-file/{session_id}/export")
async def export_data_file(session_id: str, format: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await export_data_file_for_session(
        session_id,
        format.lower(),
        allow_legacy_fallback=allow_legacy_upload_reads(user),
    )


@router.get("/api/variables/{session_id}")
async def get_variables(session_id: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await get_variables_for_session(
        session_id,
        allow_legacy_fallback=allow_legacy_upload_reads(user),
    )

