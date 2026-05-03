# -*- coding: utf-8 -*-
"""分析服务门面，负责计划、结果、报告和方法执行，别把执行细节继续塞胖。"""
import json
import os
import tempfile

from fastapi import HTTPException

from backend.ai_engine import call_deepseek, generate_plan
from backend.analysis import METHOD_REGISTRY, build_execute_params
from backend.app_runtime import download_response
from backend.database import (
    delete_result,
    get_current_dataset_version_for_session,
    get_results,
    get_session,
    rename_result,
    update_session,
)
from backend.domain import PLAN_READY, PLANNING, normalize_analysis_items
from backend.file_parser import build_data_context
from backend.services.analysis_execution_service import execute_plan_with_context, prepare_plan_execution, stream_plan_execution_with_context
from backend.services.execution_support import mark_execution_error, save_analysis_items
from backend.services.job_service import list_active_jobs_for_session
from backend.repositories.shared_report_repository import delete_shared_reports_for_overlapping_result_ids
from backend.services.session_access import get_session_or_404
from backend.services.session_data_service import load_session_dataframe
from backend.services.variable_metadata_service import inject_analysis_metadata
from backend.storage import storage_service
from backend.word_report import generate_report


async def create_plan_for_session(session_id: str, research_topic: str, variable_desc: str, hypotheses: str, analysis_request: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    await update_session(
        session_id,
        research_topic=research_topic,
        variable_desc=variable_desc,
        hypotheses=hypotheses,
        analysis_request=analysis_request,
        status=PLANNING,
    )

    data_summary = json.loads(session["data_summary"]) if session["data_summary"] else {}
    questionnaire_text = session["questionnaire_text"] or ""
    if not data_summary:
        raise HTTPException(400, "请先上传数据文件")

    try:
        plan = await generate_plan(
            data_context=build_data_context(data_summary, questionnaire_text),
            research_topic=research_topic,
            variable_desc=variable_desc,
            hypotheses=hypotheses,
            analysis_request=analysis_request,
        )
        await update_session(session_id, plan=plan, status=PLAN_READY)
        return {"plan": plan}
    except Exception as exc:
        await mark_execution_error(session_id)
        raise HTTPException(500, f"AI 生成计划失败: {str(exc)}")


async def execute_plan_for_session(session_id: str, plan_edit: str | None):
    return await execute_plan_with_context(await prepare_plan_execution(session_id, plan_edit))


async def stream_execute_plan_for_session(session_id: str, plan_edit: str | None):
    return await stream_plan_execution_with_context(await prepare_plan_execution(session_id, plan_edit))


async def get_analysis_results_for_session(session_id: str, user: dict | None = None):
    session = await (get_session_or_404(session_id, user) if user is not None else get_session(session_id))
    if not session:
        raise HTTPException(404, "会话不存在")
    jobs = []
    if user is not None:
        jobs = await list_active_jobs_for_session(session_id, user)
    current_version = await get_current_dataset_version_for_session(session_id)
    return {
        "status": session["status"],
        "results": await get_results(session_id),
        "jobs": jobs,
        "current_dataset_version_id": session.get("current_dataset_version_id"),
        "current_dataset_version_no": (current_version or {}).get("version_no"),
    }


async def rename_analysis_result_for_session(session_id: str, result_id: int, body: dict | None):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    if body is None:
        raise HTTPException(400, "请求体为空")
    new_name = (body.get("name") or "").strip()
    if not new_name:
        raise HTTPException(400, "分析结果名称不能为空")
    ok = await rename_result(session_id, result_id, new_name)
    if not ok:
        raise HTTPException(404, "分析结果不存在")
    return {"success": True, "id": result_id, "name": new_name}


async def delete_analysis_result_for_session(session_id: str, result_id: int):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    existing_results = await get_results(session_id)
    target_result = next((item for item in existing_results if int(item.get("id") or 0) == int(result_id)), None)
    ok = await delete_result(session_id, result_id)
    if not ok:
        raise HTTPException(404, "分析结果不存在")
    await delete_shared_reports_for_overlapping_result_ids(
        session_id,
        [result_id],
        report_title=str((target_result or {}).get("analysis_name") or ""),
    )
    return {"success": True, "id": result_id}


async def download_word_report_for_session(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    results = await get_results(session_id)
    if not results:
        raise HTTPException(400, "暂无分析结果")

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        temp_path = tmp.name
    try:
        generate_report(results, temp_path, title=session.get("research_topic", "") or "数据分析结果")
        with open(temp_path, "rb") as f:
            content = f.read()
        storage_service.save_bytes("outputs", session_id, "分析结果.docx", content)
        return download_response(content, "分析结果.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


async def execute_method_for_session(session_id: str, body: dict | None):
    if body is None:
        raise HTTPException(400, "请求体为空")
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    method_key = body.get("method", "")
    if method_key not in METHOD_REGISTRY:
        raise HTTPException(400, f"未知的分析方法: {method_key}")
    try:
        params = await inject_analysis_metadata(session_id, method_key, build_execute_params(method_key, body.get("params", {})))
        result = METHOD_REGISTRY[method_key](await load_session_dataframe(session_id, allow_legacy_fallback=True), params)
        items = normalize_analysis_items(result)
        await save_analysis_items(session_id, items, "[结构化执行]")
        return {"success": True, "results": items}
    except Exception as exc:
        raise HTTPException(500, f"分析执行失败: {str(exc)}")


async def interpret_analysis_result(body: dict | None):
    if body is None:
        raise HTTPException(400, "请求体为空")
    sections = body.get("sections", [])
    if not sections:
        raise HTTPException(400, "缺少分析结果数据")

    context_parts = [f"以下是「{body.get('method', '')}」的分析结果，请给出专业、详细的学术解读和建议：\n"]
    for sec in sections:
        if sec.get("type") == "table":
            context_parts.append(f"### {sec.get('title', '')}")
            headers = sec.get("headers", [])
            if headers:
                context_parts.append(" | ".join(headers))
                for row in sec.get("rows", [])[:30]:
                    context_parts.append(" | ".join(str(cell) for cell in row))
            if sec.get("note"):
                context_parts.append(sec["note"])
        elif sec.get("type") in ("advice", "smart_analysis"):
            context_parts.append(f"### {sec.get('title', '')}")
            context_parts.append(sec.get("content", ""))

    try:
        interpretation = await call_deepseek(
            [
                {"role": "system", "content": "你是一位资深的SPSS数据分析专家和统计学教授。请根据提供的分析结果，给出详细、专业的学术解读。包括：数据质量评估、核心发现、注意事项、改进建议。使用规范的学术中文撰写，条理清晰。"},
                {"role": "user", "content": "\n".join(context_parts)},
            ],
            temperature=0.3,
            max_tokens=3000,
        )
        return {"interpretation": interpretation}
    except Exception as exc:
        raise HTTPException(500, f"AI 解读失败: {str(exc)}")

