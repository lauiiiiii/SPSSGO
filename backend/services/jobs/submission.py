# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import os

from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from backend.analysis import METHOD_REGISTRY
from backend.config import DATA_EXTENSIONS, DOC_EXTENSIONS, MAX_UPLOAD_SIZE_MB
from backend.database import (
    create_job,
    get_current_dataset_version_for_session,
    get_results,
    update_job,
    update_session,
    upsert_dataset_for_session,
)
from backend.domain import ACTIVE_JOB_STATUSES, EXECUTING, PLANNING, QUEUED, SUCCEEDED
from backend.services.jobs.common import (
    dispatch_job,
    job_progress,
    json_dumps,
    queue_for_job,
    record_enqueued_job,
    result_row_to_execution_item,
    sse,
)
from backend.services.jobs.control import get_job_detail_for_user
from backend.services.session_access import get_session_or_404
from backend.storage import storage_service


async def _enqueue_job(
    job_type: str,
    owner_id: int,
    *,
    session_id: str | None = None,
    dataset_id: int | None = None,
    dataset_version_id: int | None = None,
    payload: dict | None = None,
    progress_message: str | None = None,
):
    job = await create_job(
        job_type,
        owner_id,
        queue_for_job(job_type),
        session_id=session_id,
        dataset_id=dataset_id,
        dataset_version_id=dataset_version_id,
        payload=payload or {},
        status=QUEUED,
    )
    record_enqueued_job(job)
    await update_job(job["id"], progress=job_progress("queued", progress_message or "任务已入队"))
    await dispatch_job(job)
    return job


async def submit_upload_job(session_id: str, user: dict, file: UploadFile):
    session = await get_session_or_404(session_id, user)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in DATA_EXTENSIONS | DOC_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件格式: {ext}")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"文件超过 {MAX_UPLOAD_SIZE_MB}MB 限制")

    await asyncio.to_thread(storage_service.save_bytes, "uploads", session_id, file.filename, content)
    dataset = None
    if ext in DATA_EXTENSIONS:
        dataset = await upsert_dataset_for_session(
            session_id,
            user["id"],
            file.filename,
            file.filename,
            content_type=file.content_type or "",
            size_bytes=len(content),
        )
    job = await _enqueue_job(
        "upload_ingest",
        user["id"],
        session_id=session_id,
        dataset_id=dataset["id"] if dataset else None,
        payload={
            "filename": file.filename,
            "content_type": file.content_type or "",
            "size_bytes": len(content),
        },
        progress_message="文件已接收，等待解析",
    )
    return {"accepted": True, "job_id": job["id"], "dataset_id": dataset["id"] if dataset else None, "status": job["status"]}


async def submit_process_job(session_id: str, user: dict, method: str, params: dict):
    session = await get_session_or_404(session_id, user)
    version = await get_current_dataset_version_for_session(session_id)
    if not version:
        raise HTTPException(404, "未找到标准化数据版本，请先上传数据文件")
    job = await _enqueue_job(
        "process_data",
        user["id"],
        session_id=session_id,
        dataset_id=session.get("current_dataset_id"),
        dataset_version_id=version["id"],
        payload={"method": method, "params": params or {}},
        progress_message="数据处理任务已入队",
    )
    await update_session(session_id, status=EXECUTING)
    return {"accepted": True, "job_id": job["id"], "status": job["status"]}


async def submit_execute_method_job(session_id: str, user: dict, method_key: str, params: dict):
    session = await get_session_or_404(session_id, user)
    if method_key not in METHOD_REGISTRY:
        raise HTTPException(400, f"未知的分析方法: {method_key}")
    version = await get_current_dataset_version_for_session(session_id)
    if not version:
        raise HTTPException(404, "未找到标准化数据版本，请先上传数据文件")
    job = await _enqueue_job(
        "execute_method",
        user["id"],
        session_id=session_id,
        dataset_id=session.get("current_dataset_id"),
        dataset_version_id=version["id"],
        payload={"method": method_key, "params": params or {}},
        progress_message="分析任务已入队",
    )
    await update_session(session_id, status=EXECUTING)
    return {"accepted": True, "job_id": job["id"], "status": job["status"]}


async def submit_execute_plan_job(session_id: str, user: dict, plan_edit: str | None):
    session = await get_session_or_404(session_id, user)
    plan = (plan_edit or session.get("plan") or "").strip()
    if not plan:
        raise HTTPException(400, "没有分析计划")
    if not session.get("data_summary"):
        raise HTTPException(400, "请先上传数据文件")
    version = await get_current_dataset_version_for_session(session_id)
    job = await _enqueue_job(
        "execute_plan",
        user["id"],
        session_id=session_id,
        dataset_id=session.get("current_dataset_id"),
        dataset_version_id=(version or {}).get("id"),
        payload={"plan_edit": plan},
        progress_message="整套分析任务已入队",
    )
    await update_session(session_id, plan=plan, plan_confirmed=1, status=EXECUTING)
    return {"accepted": True, "job_id": job["id"], "status": job["status"]}


async def submit_generate_report_job(session_id: str, user: dict):
    session = await get_session_or_404(session_id, user)
    results = await get_results(session_id)
    if not results:
        raise HTTPException(400, "暂无分析结果")
    job = await _enqueue_job(
        "generate_report",
        user["id"],
        session_id=session_id,
        dataset_id=session.get("current_dataset_id"),
        dataset_version_id=session.get("current_dataset_version_id"),
        payload={"filename": "分析结果.docx"},
        progress_message="报告生成任务已入队",
    )
    return {"accepted": True, "job_id": job["id"], "status": job["status"]}


async def submit_ai_plan_job(
    session_id: str,
    user: dict,
    research_topic: str,
    variable_desc: str,
    hypotheses: str,
    analysis_request: str,
):
    session = await get_session_or_404(session_id, user)
    if not session.get("data_summary"):
        raise HTTPException(400, "请先上传数据文件")

    job = await _enqueue_job(
        "ai_plan",
        user["id"],
        session_id=session_id,
        dataset_id=session.get("current_dataset_id"),
        dataset_version_id=session.get("current_dataset_version_id"),
        payload={
            "research_topic": research_topic,
            "variable_desc": variable_desc,
            "hypotheses": hypotheses,
            "analysis_request": analysis_request,
        },
        progress_message="AI 规划任务已入队",
    )
    await update_session(
        session_id,
        research_topic=research_topic,
        variable_desc=variable_desc,
        hypotheses=hypotheses,
        analysis_request=analysis_request,
        status=PLANNING,
    )
    return {"accepted": True, "job_id": job["id"], "status": job["status"]}


async def submit_ai_interpret_job(user: dict, body: dict | None):
    payload = dict(body or {})
    sections = payload.get("sections") or []
    if not sections:
        raise HTTPException(400, "缺少分析结果数据")

    session_id = payload.get("session_id") or None
    dataset_version_id = payload.get("dataset_version_id") or None
    dataset_id = None
    if session_id:
        session = await get_session_or_404(session_id, user)
        dataset_id = session.get("current_dataset_id")
        if not dataset_version_id:
            dataset_version_id = session.get("current_dataset_version_id")

    job = await _enqueue_job(
        "ai_interpret",
        user["id"],
        session_id=session_id,
        dataset_id=dataset_id,
        dataset_version_id=dataset_version_id,
        payload=payload,
        progress_message="AI 解读任务已入队",
    )
    return {"accepted": True, "job_id": job["id"], "status": job["status"]}


async def stream_execute_plan_job_events(session_id: str, user: dict, plan_edit: str | None):
    accepted = await submit_execute_plan_job(session_id, user, plan_edit)
    job_id = accepted["job_id"]

    async def event_stream():
        last_signature = None
        yield sse("accepted", accepted)
        while True:
            job = await get_job_detail_for_user(job_id, user)
            progress_payload = {
                "job_id": job["id"],
                "status": job["status"],
                "job_type": job["job_type"],
                "queue": job["queue"],
                **(job.get("progress") or {}),
            }
            signature = json_dumps([job["status"], progress_payload, job.get("error_message") or ""])
            if signature != last_signature:
                yield sse("progress", progress_payload)
                last_signature = signature
            if job["status"] not in ACTIVE_JOB_STATUSES:
                if job["status"] == SUCCEEDED:
                    rows = await get_results(session_id)
                    items = [result_row_to_execution_item(row) for row in rows if row.get("job_id") == job_id]
                    for item in items:
                        yield sse("result", item)
                    yield sse(
                        "done",
                        {
                            "success": True,
                            "job_id": job_id,
                            "mode": (job.get("result") or {}).get("mode", ""),
                            "total": len(items),
                            "dataset_version_id": job.get("dataset_version_id"),
                        },
                    )
                else:
                    yield sse(
                        "error",
                        {
                            "success": False,
                            "job_id": job_id,
                            "message": job.get("error_message") or "任务执行失败",
                        },
                    )
                return
            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
