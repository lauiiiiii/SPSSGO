# -*- coding: utf-8 -*-
"""作业执行辅助模块，只放 upload_ingest / process_data / ai_interpret 的细碎编排。"""
from __future__ import annotations

import asyncio
import json

from backend.ai_engine import call_deepseek
from backend.database import get_dataset_for_session, get_session_for_user, update_job, update_session
from backend.domain import CREATED
from backend.file_parser import parse_data_file_async
from backend.processing import run_process_method
from backend.services.dataset_version_service import create_dataset_version_from_dataframe, save_current_metadata_snapshot
from backend.services.jobs.common import job_progress
from backend.services.variable_metadata_service import persist_processing_metadata
from backend.services.upload_ingest_service import load_questionnaire_content
from backend.storage import storage_service


async def run_questionnaire_ingest(job: dict, filename: str) -> dict:
    session_id = job["session_id"]
    content = await asyncio.to_thread(load_questionnaire_content, session_id, filename)
    session = await get_session_for_user(session_id, job["owner_id"], is_admin=True)
    previous = (session or {}).get("questionnaire_text") or ""
    text = content.get("content", "")
    combined = (previous + "\n\n--- " + filename + " ---\n" + text).strip()
    await update_session(session_id, questionnaire_text=combined, status=CREATED)
    return {"filename": filename, "questionnaire_preview": text[:500]}


async def run_dataset_ingest(job: dict, filename: str) -> dict:
    session_id = job["session_id"]
    path = storage_service.materialize_file("uploads", session_id, filename)
    try:
        df, summary = await parse_data_file_async(path)
        version, _ = await create_dataset_version_from_dataframe(
            session_id,
            job["owner_id"],
            df,
            source_job_id=job["id"],
        )
        dataset = await get_dataset_for_session(session_id)
        await save_current_metadata_snapshot(session_id, version["storage_key"])
        await update_job(
            job["id"],
            dataset_version_id=version["id"],
            progress=job_progress("ingested", "数据已解析并生成标准化版本", dataset_version_id=version["id"]),
        )
        await update_session(session_id, status=CREATED)
        return {
            "filename": filename,
            "dataset_id": dataset["id"],
            "dataset_version_id": version["id"],
            "data_summary": summary,
        }
    finally:
        storage_service.release_materialized(path)


async def run_process_data_job(
    job: dict,
    version: dict,
    dataset: dict,
    materialize_dataset,
) -> dict:
    session_id = job["session_id"]
    payload = job["payload"]
    if not version or not dataset:
        raise RuntimeError("当前会话缺少可处理的数据版本")
    with materialize_dataset(session_id, version["storage_key"]) as filepath:
        df, _ = await parse_data_file_async(filepath)
    try:
        next_df, message = await asyncio.to_thread(
            run_process_method,
            df,
            payload["method"],
            payload.get("params") or {},
        )
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc
    next_version, summary = await create_dataset_version_from_dataframe(
        session_id,
        job["owner_id"],
        next_df,
        source_job_id=job["id"],
    )
    await persist_processing_metadata(session_id, payload["method"], payload.get("params") or {})
    await save_current_metadata_snapshot(session_id, next_version["storage_key"])
    await update_session(session_id, status=CREATED)
    return {
        "success": True,
        "message": message,
        "total_rows": int(summary.get("row_count") or len(next_df)),
        "dataset_version_id": next_version["id"],
        "dataset_version_no": next_version["version_no"],
    }


def build_interpretation_prompt(payload: dict) -> tuple[str, list[dict]]:
    sections = payload.get("sections") or []
    method_name = payload.get("method", "")
    context_parts = [f"以下是「{method_name}」的分析结果，请给出专业、详细的学术解读和建议：\n"]
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
        elif sec.get("type") in {"advice", "smart_analysis"}:
            context_parts.append(f"### {sec.get('title', '')}")
            context_parts.append(sec.get("content", ""))
    return method_name, [
        {
            "role": "system",
            "content": "你是一位资深的SPSS数据分析专家和统计学教授。请根据提供的分析结果，给出详细、专业的学术解读。包括：数据质量评估、核心发现、注意事项、改进建议。使用规范的学术中文撰写，条理清晰。",
        },
        {"role": "user", "content": "\n".join(context_parts)},
    ]


async def run_ai_interpretation(job: dict) -> dict:
    payload = job["payload"] or {}
    sections = payload.get("sections") or []
    if not sections:
        raise RuntimeError("缺少分析结果数据")

    method_name, messages = build_interpretation_prompt(payload)
    await update_job(job["id"], progress=job_progress("interpreting", "AI 正在生成解读"))
    interpretation = await call_deepseek(
        messages,
        temperature=0.3,
        max_tokens=3000,
    )
    return {"interpretation": interpretation, "method": method_name, "section_count": len(sections)}
