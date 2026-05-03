# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import os

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from backend.app_runtime import download_response
from backend.database import (
    create_job,
    get_job,
    get_job_for_user,
    list_jobs_for_session,
    list_sandbox_executions_for_job,
    update_job,
    update_session,
)
from backend.domain import ACTIVE_JOB_STATUSES, CANCELED, EXECUTING, FAILED, PLANNING, QUEUED, RETRYING, RUNNING, SUCCEEDED
from backend.services.jobs.common import (
    cancel_job_execution,
    dispatch_job,
    finalize_canceled_job,
    job_progress,
    job_snapshot,
    json_dumps,
    queued_message_for_job,
    record_enqueued_job,
    sse,
    time_now,
)
from backend.storage import storage_service


async def get_job_detail_for_user(job_id: str, user: dict):
    job = await get_job_for_user(job_id, user["id"], is_admin=user.get("role") == "admin")
    if not job:
        raise HTTPException(404, "任务不存在")
    return job


async def list_sandbox_runs_for_user(job_id: str, user: dict):
    await get_job_detail_for_user(job_id, user)
    return await list_sandbox_executions_for_job(job_id)


async def stream_job_events(job_id: str, user: dict):
    async def event_stream():
        last_signature = None
        while True:
            job = await get_job_detail_for_user(job_id, user)
            payload = job_snapshot(job)
            signature = json_dumps(payload)
            if signature != last_signature:
                yield sse("job", payload)
                last_signature = signature
            if job["status"] not in ACTIVE_JOB_STATUSES:
                yield sse("done", payload)
                return
            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def list_active_jobs_for_session(session_id: str, user: dict):
    return await list_jobs_for_session(
        session_id,
        owner_id=user["id"],
        is_admin=user.get("role") == "admin",
        statuses=ACTIVE_JOB_STATUSES,
    )


async def download_job_output(job_id: str, user: dict):
    job = await get_job_detail_for_user(job_id, user)
    if job["status"] != SUCCEEDED:
        raise HTTPException(409, "任务尚未完成")
    result = job.get("result") or {}
    storage_key = result.get("storage_key")
    if not storage_key:
        raise HTTPException(404, "当前任务没有可下载产物")
    session_id = job.get("session_id")
    if not session_id or not storage_service.exists("outputs", session_id, storage_key):
        raise HTTPException(404, "任务产物不存在")
    filename = result.get("filename") or os.path.basename(storage_key)
    media_type = result.get("media_type") or "application/octet-stream"
    content = storage_service.read_bytes("outputs", session_id, storage_key)
    return download_response(content, filename, media_type)


async def cancel_job_for_user(job_id: str, user: dict):
    job = await get_job_detail_for_user(job_id, user)
    if job["status"] == CANCELED:
        return {"success": True, "already_canceled": True, "job": job_snapshot(job)}
    if job["status"] in {SUCCEEDED, FAILED}:
        raise HTTPException(409, "当前任务已结束，无法取消")

    await cancel_job_execution(job)
    await update_job(
        job_id,
        status=CANCELED,
        error_message="任务已取消",
        finished_at=time_now(),
        progress=job_progress("canceled", "任务已取消"),
    )
    current = await get_job(job_id) or job
    await finalize_canceled_job(current)
    current = await get_job(job_id) or current
    return {"success": True, "job": job_snapshot(current)}


async def retry_job_for_user(job_id: str, user: dict):
    job = await get_job_detail_for_user(job_id, user)
    if job["status"] not in {FAILED, CANCELED}:
        raise HTTPException(409, "只有失败或已取消的任务才能重试")

    next_job = await create_job(
        job["job_type"],
        job["owner_id"],
        job["queue"],
        session_id=job.get("session_id"),
        dataset_id=job.get("dataset_id"),
        dataset_version_id=job.get("dataset_version_id"),
        payload=job.get("payload") or {},
        status=RETRYING,
    )
    await update_job(
        next_job["id"],
        status=QUEUED,
        progress=job_progress("queued", queued_message_for_job(job["job_type"]), retry_of=job["id"]),
    )
    next_job = await get_job(next_job["id"]) or next_job
    record_enqueued_job(next_job)
    if next_job.get("session_id"):
        if next_job["job_type"] in {"process_data", "execute_method", "execute_plan"}:
            await update_session(next_job["session_id"], status=EXECUTING)
        elif next_job["job_type"] == "ai_plan":
            await update_session(next_job["session_id"], status=PLANNING)
    await dispatch_job(next_job)
    return {
        "success": True,
        "source_job_id": job["id"],
        "job_id": next_job["id"],
        "job": job_snapshot(next_job),
    }
