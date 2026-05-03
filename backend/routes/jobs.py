# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from backend.admin_auth import current_user_required
from backend.services.job_service import (
    cancel_job_for_user,
    download_job_output,
    get_job_detail_for_user,
    list_sandbox_runs_for_user,
    retry_job_for_user,
    stream_job_events,
)

router = APIRouter()


@router.get("/api/jobs/{job_id}")
async def get_job_detail(job_id: str, user=Depends(current_user_required)):
    return await get_job_detail_for_user(job_id, user)


@router.get("/api/jobs/{job_id}/events")
async def get_job_events(job_id: str, user=Depends(current_user_required)):
    return await stream_job_events(job_id, user)


@router.get("/api/jobs/{job_id}/sandbox-runs")
async def get_job_sandbox_runs(job_id: str, user=Depends(current_user_required)):
    return await list_sandbox_runs_for_user(job_id, user)


@router.get("/api/jobs/{job_id}/output")
async def get_job_output(job_id: str, user=Depends(current_user_required)):
    return await download_job_output(job_id, user)


@router.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, user=Depends(current_user_required)):
    return await cancel_job_for_user(job_id, user)


@router.post("/api/jobs/{job_id}/retry")
async def retry_job(job_id: str, user=Depends(current_user_required)):
    return await retry_job_for_user(job_id, user)
