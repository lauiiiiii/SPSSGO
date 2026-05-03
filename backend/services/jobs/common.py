# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json
import time

from backend.config import (
    FAULT_INJECTION_JOB_DELAY_SECONDS,
    FAULT_INJECTION_JOB_DELAY_TYPES,
    JOB_BACKEND,
)
from backend.database import (
    cancel_active_sandbox_executions_for_job,
    delete_results_for_job,
    get_job,
    get_results,
    list_jobs_for_session,
    update_job,
    update_session,
)
from backend.domain import ACTIVE_JOB_STATUSES, CANCELED, CREATED, DONE, SUCCEEDED
from backend.observability import record_job_submission, record_job_transition

_LOCAL_JOB_TASKS: dict[str, asyncio.Task] = {}


def job_progress(stage: str, message: str, **extra):
    payload = {"stage": stage, "message": message}
    payload.update(extra)
    return payload


def record_enqueued_job(job: dict):
    record_job_submission(job["job_type"], job["queue"])
    record_job_transition(job["job_type"], job["queue"], job["status"])


def queue_for_job(job_type: str) -> str:
    if job_type == "upload_ingest":
        return "ingest"
    if job_type == "process_data":
        return "process"
    if job_type in {"execute_method", "execute_plan"}:
        return "analysis"
    if job_type in {"ai_plan", "ai_interpret"}:
        return "ai"
    if job_type == "generate_report":
        return "report"
    return "default"


def queued_message_for_job(job_type: str) -> str:
    if job_type == "upload_ingest":
        return "文件已接收，等待解析"
    if job_type == "process_data":
        return "数据处理任务已入队"
    if job_type == "ai_plan":
        return "AI 规划任务已入队"
    if job_type == "ai_interpret":
        return "AI 解读任务已入队"
    if job_type == "execute_method":
        return "分析任务已入队"
    if job_type == "execute_plan":
        return "整套分析任务已入队"
    if job_type == "generate_report":
        return "报告生成任务已入队"
    return "任务已入队"


def json_dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def json_loads(value, default):
    if not value:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


def time_now() -> float:
    return time.time()


def job_snapshot(job: dict) -> dict:
    return {
        "id": job["id"],
        "job_type": job["job_type"],
        "status": job["status"],
        "queue": job["queue"],
        "progress": job.get("progress") or {},
        "result": job.get("result") or {},
        "error_message": job.get("error_message") or "",
        "session_id": job.get("session_id"),
        "dataset_id": job.get("dataset_id"),
        "dataset_version_id": job.get("dataset_version_id"),
        "created_at": job.get("created_at"),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
    }


def result_row_to_execution_item(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "name": row.get("analysis_name") or "",
        "headers": row.get("table_headers") or [],
        "rows": row.get("table_rows") or [],
        "description": row.get("description") or "",
        "sections": row.get("sections") or None,
    }


def sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json_dumps(payload)}\n\n"


def should_apply_fault_injection_delay(job_type: str) -> bool:
    if FAULT_INJECTION_JOB_DELAY_SECONDS <= 0:
        return False
    if not FAULT_INJECTION_JOB_DELAY_TYPES:
        return True
    normalized = (job_type or "").strip().lower()
    return "all" in FAULT_INJECTION_JOB_DELAY_TYPES or normalized in FAULT_INJECTION_JOB_DELAY_TYPES


async def maybe_fault_injection_delay(job: dict):
    if not should_apply_fault_injection_delay(job.get("job_type") or ""):
        return
    delay_seconds = max(float(FAULT_INJECTION_JOB_DELAY_SECONDS), 0.0)
    await update_job(
        job["id"],
        progress=job_progress(
            "fault_injection_delay",
            f"故障演练延迟 {delay_seconds:.1f}s，任务即将继续执行",
            delay_seconds=delay_seconds,
        ),
    )
    await asyncio.sleep(delay_seconds)


async def dispatch_job(job: dict):
    if JOB_BACKEND == "celery":
        try:
            from backend.worker_tasks import execute_job_task

            task = execute_job_task.apply_async(args=[job["id"]], queue=job["queue"])
            await update_job(job["id"], celery_task_id=task.id)
            return
        except Exception:
            pass
    from backend.services.jobs.runner import run_job

    task = asyncio.create_task(run_job(job["id"]))
    _LOCAL_JOB_TASKS[job["id"]] = task
    task.add_done_callback(lambda _task, job_id=job["id"]: _LOCAL_JOB_TASKS.pop(job_id, None))


async def cancel_job_execution(job: dict):
    task = _LOCAL_JOB_TASKS.get(job["id"])
    if task and not task.done():
        task.cancel()

    if JOB_BACKEND != "celery" or not job.get("celery_task_id"):
        return
    try:
        from backend.celery_app import celery_app

        if celery_app is not None:
            celery_app.control.revoke(job["celery_task_id"], terminate=True)
    except Exception:
        pass


async def sync_session_status_if_idle(session_id: str | None):
    if not session_id:
        return
    active_jobs = await list_jobs_for_session(session_id, is_admin=True, statuses=ACTIVE_JOB_STATUSES, limit=50)
    if active_jobs:
        return
    results = await get_results(session_id)
    await update_session(session_id, status=DONE if results else CREATED)


async def finalize_canceled_job(job: dict):
    if job["job_type"] in {"execute_method", "execute_plan"}:
        await delete_results_for_job(job["id"])
    await cancel_active_sandbox_executions_for_job(job["id"])
    await sync_session_status_if_idle(job.get("session_id"))


async def finalize_run_cancellation(job_id: str, user_job: dict):
    current = await get_job(job_id) or user_job
    if current["status"] != CANCELED:
        await update_job(
            job_id,
            status=CANCELED,
            error_message="任务已取消",
            finished_at=time_now(),
            progress=job_progress("canceled", "任务已取消"),
        )
        current = await get_job(job_id) or current
    await finalize_canceled_job(current)
    record_job_transition(user_job["job_type"], user_job["queue"], CANCELED)

