# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import os
import tempfile
from contextlib import contextmanager

from backend.ai_engine import generate_plan
from backend.analysis import METHOD_REGISTRY, build_execute_params
from backend.analysis.common import append_optional_missing_analysis
from backend.database import (
    delete_results_for_job,
    get_current_dataset_version_for_session,
    get_dataset_for_session,
    get_dataset_version,
    get_job,
    get_results,
    get_session,
    get_session_for_user,
    save_result,
    update_job,
    update_session,
)
from backend.domain import CANCELED, CREATED, DONE, ERROR, FAILED, EXECUTING, PLAN_READY, RUNNING, SUCCEEDED, normalize_analysis_items
from backend.file_parser import build_data_context, parse_data_file_async
from backend.observability import finish_job_execution, record_job_transition, start_job_execution
from backend.runtime_control import session_write_lock
from backend.services.jobs.aux_runner import (
    run_ai_interpretation,
    run_dataset_ingest,
    run_process_data_job,
    run_questionnaire_ingest,
)
from backend.services.jobs.common import (
    finalize_run_cancellation,
    job_progress,
    json_loads,
    maybe_fault_injection_delay,
    sync_session_status_if_idle,
    time_now,
)
from backend.services.jobs.plan_runner import build_plan_execution_context, run_generated_plan_job, try_run_template_plan_job
from backend.services.variable_metadata_service import inject_analysis_metadata
from backend.storage import storage_service
from backend.word_report import generate_report

_REPORT_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@contextmanager
def _materialized_dataset(session_id: str, storage_key: str):
    path = storage_service.materialize_file("datasets", session_id, storage_key)
    try:
        yield path
    finally:
        storage_service.release_materialized(path)


async def run_job(job_id: str):
    user_job = await get_job(job_id)
    if not user_job:
        return
    if user_job["status"] == CANCELED:
        await sync_session_status_if_idle(user_job.get("session_id"))
        return
    execution_started_at = time_now()
    running_metric = start_job_execution(user_job["job_type"], user_job["queue"])
    record_job_transition(user_job["job_type"], user_job["queue"], RUNNING)
    await update_job(
        job_id,
        status=RUNNING,
        attempts=int(user_job.get("attempts") or 0) + 1,
        started_at=execution_started_at,
        progress=job_progress("running", "任务开始执行"),
    )
    try:
        await maybe_fault_injection_delay(user_job)
        if user_job["job_type"] == "upload_ingest":
            result = await _run_upload_ingest_job(user_job)
        elif user_job["job_type"] == "process_data":
            result = await _run_process_job(user_job)
        elif user_job["job_type"] == "ai_plan":
            result = await _run_ai_plan_job(user_job)
        elif user_job["job_type"] == "ai_interpret":
            result = await _run_ai_interpret_job(user_job)
        elif user_job["job_type"] == "execute_method":
            result = await _run_execute_method_job(user_job)
        elif user_job["job_type"] == "execute_plan":
            result = await _run_execute_plan_job(user_job)
        elif user_job["job_type"] == "generate_report":
            result = await _run_generate_report_job(user_job)
        else:
            raise RuntimeError(f"未知任务类型: {user_job['job_type']}")
        current = await get_job(job_id)
        if current and current["status"] == CANCELED:
            await finalize_run_cancellation(job_id, user_job)
            return
        await update_job(
            job_id,
            status=SUCCEEDED,
            result=result,
            error_message="",
            finished_at=time_now(),
            progress=job_progress("completed", "任务执行完成"),
        )
        record_job_transition(user_job["job_type"], user_job["queue"], SUCCEEDED)
        finish_job_execution(running_metric, user_job["job_type"], user_job["queue"], SUCCEEDED, time_now() - execution_started_at)
    except asyncio.CancelledError:
        await finalize_run_cancellation(job_id, user_job)
        finish_job_execution(running_metric, user_job["job_type"], user_job["queue"], CANCELED, time_now() - execution_started_at)
    except Exception as exc:
        current = await get_job(job_id)
        if current and current["status"] == CANCELED:
            await finalize_run_cancellation(job_id, user_job)
            finish_job_execution(running_metric, user_job["job_type"], user_job["queue"], CANCELED, time_now() - execution_started_at)
            return
        await update_job(
            job_id,
            status=FAILED,
            error_message=str(exc),
            finished_at=time_now(),
            progress=job_progress("failed", str(exc)),
        )
        record_job_transition(user_job["job_type"], user_job["queue"], FAILED)
        finish_job_execution(running_metric, user_job["job_type"], user_job["queue"], FAILED, time_now() - execution_started_at)
        if user_job.get("session_id") and user_job["job_type"] in {"upload_ingest", "process_data", "ai_plan", "execute_method", "execute_plan"}:
            await update_session(user_job["session_id"], status=ERROR)


async def _run_upload_ingest_job(job: dict):
    from backend.config import DOC_EXTENSIONS, SESSION_WRITE_LOCK_TTL_SECONDS

    session_id = job["session_id"]
    payload = job["payload"]
    filename = payload["filename"]
    ext = os.path.splitext(filename)[1].lower()
    async with session_write_lock(
        session_id,
        holder=f"upload_ingest:{job['id']}",
        ttl_seconds=SESSION_WRITE_LOCK_TTL_SECONDS,
        wait_timeout=None,
    ):
        if ext in DOC_EXTENSIONS:
            return await run_questionnaire_ingest(job, filename)
        return await run_dataset_ingest(job, filename)


async def _run_process_job(job: dict):
    from backend.config import SESSION_WRITE_LOCK_TTL_SECONDS

    session_id = job["session_id"]
    payload = job["payload"]
    async with session_write_lock(
        session_id,
        holder=f"process_data:{job['id']}",
        ttl_seconds=SESSION_WRITE_LOCK_TTL_SECONDS,
        wait_timeout=None,
    ):
        version = await get_dataset_version(job.get("dataset_version_id")) or await get_current_dataset_version_for_session(session_id)
        dataset = await get_dataset_for_session(session_id)
        return await run_process_data_job(job, version, dataset, _materialized_dataset)


async def _run_ai_plan_job(job: dict):
    session_id = job["session_id"]
    session = await get_session(session_id)
    if not session:
        raise RuntimeError("会话不存在")

    payload = job["payload"] or {}
    research_topic = payload.get("research_topic", "")
    variable_desc = payload.get("variable_desc", "")
    hypotheses = payload.get("hypotheses", "")
    analysis_request = payload.get("analysis_request", "")
    data_summary = json_loads(session.get("data_summary"), {})
    questionnaire_text = session.get("questionnaire_text") or ""
    if not data_summary:
        raise RuntimeError("请先上传数据文件")

    await update_job(job["id"], progress=job_progress("planning", "AI 正在理解研究问题并生成计划"))
    plan = await generate_plan(
        data_context=build_data_context(data_summary, questionnaire_text),
        research_topic=research_topic,
        variable_desc=variable_desc,
        hypotheses=hypotheses,
        analysis_request=analysis_request,
    )
    await update_session(session_id, plan=plan, status=PLAN_READY)
    return {
        "plan": plan,
        "research_topic": research_topic,
        "variable_desc": variable_desc,
        "hypotheses": hypotheses,
        "analysis_request": analysis_request,
    }


async def _run_ai_interpret_job(job: dict):
    return await run_ai_interpretation(job)


async def _run_execute_method_job(job: dict):
    session_id = job["session_id"]
    payload = job["payload"]
    version = await get_dataset_version(job.get("dataset_version_id")) or await get_current_dataset_version_for_session(session_id)
    if not version:
        raise RuntimeError("当前会话缺少可分析的数据版本")
    with _materialized_dataset(session_id, version["storage_key"]) as filepath:
        df, _ = await parse_data_file_async(filepath)
    params = await inject_analysis_metadata(session_id, payload["method"], build_execute_params(payload["method"], payload.get("params") or {}))
    result = await asyncio.to_thread(METHOD_REGISTRY[payload["method"]], df, params)
    result = append_optional_missing_analysis(result, df, params)
    items = normalize_analysis_items(result)
    await delete_results_for_job(job["id"])
    for item in items:
        await save_result(
            session_id=session_id,
            analysis_name=item["name"],
            table_headers=item["headers"],
            table_rows=item["rows"],
            description=item["description"],
            code="[异步作业执行]",
            sections=item["sections"],
            owner_id=job["owner_id"],
            job_id=job["id"],
            dataset_version_id=version["id"],
        )
    await update_session(session_id, status=DONE)
    return {"success": True, "count": len(items), "dataset_version_id": version["id"]}


async def _run_execute_plan_job(job: dict):
    session_id = job["session_id"]
    session = await get_session(session_id)
    if not session:
        raise RuntimeError("会话不存在")
    plan = (job["payload"].get("plan_edit") or session.get("plan") or "").strip()
    if not plan:
        raise RuntimeError("没有分析计划")
    version = await get_dataset_version(job.get("dataset_version_id")) or await get_current_dataset_version_for_session(session_id)
    if not version:
        raise RuntimeError("当前会话缺少可分析的数据版本")

    await update_session(session_id, plan=plan, plan_confirmed=1, status=EXECUTING)
    context = build_plan_execution_context(session, version, plan)
    context["storage_key"] = version["storage_key"]

    await update_job(job["id"], progress=job_progress("planning", "AI 正在解析计划并生成任务配置"))
    with _materialized_dataset(session_id, version["storage_key"]) as filepath:
        template_result = await try_run_template_plan_job(job, context, filepath, version["id"], _save_job_results)
        if template_result is not None:
            return template_result
        return await run_generated_plan_job(job, context, filepath, version["id"], _save_job_results)


async def _run_generate_report_job(job: dict):
    session_id = job["session_id"]
    session = await get_session(session_id)
    if not session:
        raise RuntimeError("会话不存在")
    results = await get_results(session_id)
    if not results:
        raise RuntimeError("暂无分析结果")

    filename = (job["payload"].get("filename") or "分析结果.docx").strip() or "分析结果.docx"
    await update_job(job["id"], progress=job_progress("rendering", "正在生成 Word 报告"))
    content = await asyncio.to_thread(_render_report_content, results, session.get("research_topic", "") or "数据分析结果")

    storage_key = f"{job['id']}-{filename}"
    await asyncio.to_thread(storage_service.save_bytes, "outputs", session_id, storage_key, content)
    return {
        "success": True,
        "filename": filename,
        "storage_key": storage_key,
        "media_type": _REPORT_MEDIA_TYPE,
        "size_bytes": len(content),
    }


async def _save_job_results(job: dict, items: list[dict], code: str, dataset_version_id: int):
    for item in items:
        await save_result(
            session_id=job["session_id"],
            analysis_name=item["name"],
            table_headers=item["headers"],
            table_rows=item["rows"],
            description=item["description"],
            code=code,
            sections=item["sections"],
            owner_id=job["owner_id"],
            job_id=job["id"],
            dataset_version_id=dataset_version_id,
        )


def _render_report_content(results: list[dict], title: str) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        temp_path = tmp.name
    try:
        generate_report(results, temp_path, title=title)
        with open(temp_path, "rb") as handle:
            return handle.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
