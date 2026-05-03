# -*- coding: utf-8 -*-
"""沙箱执行服务，只管代码执行和审计，别把分析结果落库细节塞进来。"""
import asyncio
import time

from backend.app_runtime import get_executor
from backend.code_executor import execute_analysis_code
from backend.config import JOB_BACKEND, MAX_EXECUTION_SECONDS
from backend.database import create_sandbox_execution, update_sandbox_execution
from backend.observability import record_sandbox_execution
from backend.storage import storage_service


async def start_sandbox_audit(
    audit_context: dict | None,
    *,
    backend: str,
    queue: str = "sandbox",
    status: str = "running",
    celery_task_id: str | None = None,
):
    if not audit_context:
        return None
    return await create_sandbox_execution(
        audit_context["job_id"],
        audit_context["owner_id"],
        session_id=audit_context.get("session_id"),
        dataset_version_id=audit_context.get("dataset_version_id"),
        celery_task_id=celery_task_id,
        queue=queue,
        status=status,
        data_storage_key=audit_context.get("data_storage_key"),
        details={
            "backend": backend,
            "stage": audit_context.get("stage"),
            "attempt": audit_context.get("attempt"),
        },
        started_at=time.time(),
    )


async def finish_sandbox_audit(execution: dict | None, result: dict | None, error_message: str | None = None):
    if not execution:
        return
    audit = (result or {}).get("audit") or {}
    current_details = dict(execution.get("details") or {})
    current_details.update(audit)
    status = "succeeded" if result and result.get("success") else "failed"
    if error_message:
        status = "failed"
    duration_seconds = None
    finished_at = time.time()
    started_at = execution.get("started_at")
    if started_at is not None:
        duration_seconds = max(0.0, finished_at - float(started_at))
    await update_sandbox_execution(
        execution["execution_id"],
        status=status,
        executor_mode=audit.get("executor_mode") or execution.get("executor_mode"),
        docker_image=audit.get("docker_image") or execution.get("docker_image"),
        container_name=audit.get("container_name") or execution.get("container_name"),
        exit_code=audit.get("exit_code"),
        error_message=error_message or (result or {}).get("error") or "",
        finished_at=finished_at,
        details=current_details,
    )
    record_sandbox_execution(
        audit.get("executor_mode") or execution.get("executor_mode"),
        status,
        duration_seconds,
    )


async def run_code_in_sandbox(
    code: str,
    *,
    data_file: str | None = None,
    storage_category: str | None = None,
    session_id: str | None = None,
    storage_key: str | None = None,
    owner_id: int | None = None,
    dataset_version_id: int | None = None,
    parent_job_id: str | None = None,
    stage: str = "generated",
    attempt: int | None = None,
):
    audit_context = _build_sandbox_audit_context(
        parent_job_id=parent_job_id,
        owner_id=owner_id,
        session_id=session_id,
        dataset_version_id=dataset_version_id,
        storage_key=storage_key,
        stage=stage,
        attempt=attempt,
    )

    if JOB_BACKEND == "celery" and storage_category and session_id and storage_key:
        try:
            from backend.worker_tasks import execute_sandbox_code_task

            task = execute_sandbox_code_task.apply_async(
                args=[code, storage_category, session_id, storage_key, audit_context],
                queue="sandbox",
            )
            return await asyncio.to_thread(_wait_for_sandbox_result, task)
        except Exception:
            pass

    local_execution = await _start_local_sandbox_audit(audit_context)
    if data_file:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(get_executor(), execute_analysis_code, code, data_file)
        except Exception as exc:
            await _finish_local_sandbox_audit(local_execution, None, str(exc))
            raise
        await _finish_local_sandbox_audit(local_execution, result)
        return result

    if storage_category and session_id and storage_key:
        path = storage_service.materialize_file(storage_category, session_id, storage_key)
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(get_executor(), execute_analysis_code, code, path)
            await _finish_local_sandbox_audit(local_execution, result)
            return result
        except Exception as exc:
            await _finish_local_sandbox_audit(local_execution, None, str(exc))
            raise
        finally:
            storage_service.release_materialized(path)

    await _finish_local_sandbox_audit(local_execution, None, "缺少可执行代码的数据文件上下文")
    raise RuntimeError("缺少可执行代码的数据文件上下文")


def _wait_for_sandbox_result(task):
    try:
        from celery.result import allow_join_result
    except Exception:
        allow_join_result = None

    if allow_join_result is not None:
        with allow_join_result():
            return task.get(timeout=MAX_EXECUTION_SECONDS + 15, disable_sync_subtasks=False)
    return task.get(timeout=MAX_EXECUTION_SECONDS + 15, disable_sync_subtasks=False)


def _build_sandbox_audit_context(
    *,
    parent_job_id: str | None,
    owner_id: int | None,
    session_id: str | None,
    dataset_version_id: int | None,
    storage_key: str | None,
    stage: str,
    attempt: int | None,
) -> dict | None:
    if not parent_job_id or not owner_id:
        return None
    return {
        "job_id": parent_job_id,
        "owner_id": owner_id,
        "session_id": session_id,
        "dataset_version_id": dataset_version_id,
        "data_storage_key": storage_key,
        "stage": stage,
        "attempt": attempt,
    }


async def _start_local_sandbox_audit(audit_context: dict | None):
    return await start_sandbox_audit(
        audit_context,
        backend="local",
    )


async def _finish_local_sandbox_audit(execution: dict | None, result: dict | None, error_message: str | None = None):
    await finish_sandbox_audit(execution, result, error_message)
