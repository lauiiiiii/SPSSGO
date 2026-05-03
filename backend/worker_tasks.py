# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import time

from backend.celery_app import celery_app
from backend.code_executor import execute_analysis_code
from backend.config import validate_runtime_config
from backend.database import init_db, update_job
from backend.observability import init_observability
from backend.services.job_service import run_job
from backend.services.sandbox_service import finish_sandbox_audit, start_sandbox_audit
from backend.storage import storage_service


async def _initialize_worker_runtime():
    init_observability()
    validate_runtime_config()
    await init_db()
    storage_service.initialize()


async def _run_worker_job(job_id: str):
    await _initialize_worker_runtime()
    await run_job(job_id)


async def _mark_job_failed(job_id: str, exc: Exception):
    try:
        await init_db()
        await update_job(
            job_id,
            status="failed",
            error_message=str(exc),
            finished_at=time.time(),
            progress={"stage": "worker_failed", "message": str(exc)},
        )
    except Exception:
        pass


async def _run_worker_job_with_failure_sync(job_id: str):
    try:
        await _run_worker_job(job_id)
    except Exception as exc:
        await _mark_job_failed(job_id, exc)
        raise


if celery_app is not None:
    @celery_app.task(name="spssgo.execute_job")
    def execute_job_task(job_id: str):
        asyncio.run(_run_worker_job_with_failure_sync(job_id))

    @celery_app.task(bind=True, name="spssgo.execute_sandbox_code")
    def execute_sandbox_code_task(self, code: str, category: str, session_id: str, relative_path: str, audit_context: dict | None = None):
        asyncio.run(_initialize_worker_runtime())
        normalized_audit_context = dict(audit_context or {})
        if normalized_audit_context:
            normalized_audit_context.setdefault("session_id", session_id)
            normalized_audit_context.setdefault("data_storage_key", relative_path)
        execution = asyncio.run(
            start_sandbox_audit(
                normalized_audit_context,
                backend="celery",
                celery_task_id=getattr(self.request, "id", None),
            )
        )
        try:
            path = storage_service.materialize_file(category, session_id, relative_path)
        except Exception as exc:
            if execution:
                asyncio.run(finish_sandbox_audit(execution, None, str(exc)))
            raise
        try:
            result = execute_analysis_code(code, path)
            if execution:
                asyncio.run(finish_sandbox_audit(execution, result))
            return result
        except Exception as exc:
            if execution:
                asyncio.run(finish_sandbox_audit(execution, None, str(exc)))
            raise
        finally:
            storage_service.release_materialized(path)
else:  # pragma: no cover - fallback for environments without Celery installed
    class _MissingCeleryTask:
        def delay(self, *_args, **_kwargs):
            raise RuntimeError("Celery is not installed")

    execute_job_task = _MissingCeleryTask()
    execute_sandbox_code_task = _MissingCeleryTask()
