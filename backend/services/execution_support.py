# -*- coding: utf-8 -*-
"""分析执行支撑层，只放任务生成、结果落库和会话状态切换。"""

from backend.ai_engine import generate_code, generate_tasks_json
from backend.database import save_result, update_session
from backend.domain import DONE, ERROR, normalize_analysis_items
from backend.services.sandbox_service import run_code_in_sandbox
from backend.template_executor import parse_ai_tasks


async def save_analysis_items(session_id: str, items, code: str):
    for item in normalize_analysis_items(items):
        await save_result(
            session_id=session_id,
            analysis_name=item["name"],
            table_headers=item["headers"],
            table_rows=item["rows"],
            description=item["description"],
            code=code,
            sections=item["sections"],
        )


async def generate_analysis_tasks(data_context: dict, plan: str, research_info: str):
    response = await generate_tasks_json(data_context=data_context, plan=plan, research_info=research_info)
    return parse_ai_tasks(response)


async def execute_generated_custom_code(
    data_context: dict,
    research_info: str,
    custom_desc: str,
    data_file: str,
    *,
    storage_category: str | None = None,
    session_id: str | None = None,
    storage_key: str | None = None,
    owner_id: int | None = None,
    dataset_version_id: int | None = None,
    parent_job_id: str | None = None,
):
    code = await generate_code(data_context=data_context, plan=custom_desc, research_info=research_info)
    result = await run_code_in_sandbox(
        code,
        data_file=data_file,
        storage_category=storage_category,
        session_id=session_id,
        storage_key=storage_key,
        owner_id=owner_id,
        dataset_version_id=dataset_version_id,
        parent_job_id=parent_job_id,
        stage="custom",
    )
    return result, code


async def run_generated_analysis_code(
    data_context: dict,
    plan: str,
    research_info: str,
    data_file: str,
    error_feedback: str = "",
    *,
    storage_category: str | None = None,
    session_id: str | None = None,
    storage_key: str | None = None,
    owner_id: int | None = None,
    dataset_version_id: int | None = None,
    parent_job_id: str | None = None,
    stage: str = "generated",
    attempt: int | None = None,
):
    code = await generate_code(
        data_context=data_context,
        plan=plan,
        research_info=research_info,
        error_feedback=error_feedback,
    )
    result = await run_code_in_sandbox(
        code,
        data_file=data_file,
        storage_category=storage_category,
        session_id=session_id,
        storage_key=storage_key,
        owner_id=owner_id,
        dataset_version_id=dataset_version_id,
        parent_job_id=parent_job_id,
        stage=stage,
        attempt=attempt,
    )
    return result, code


async def mark_execution_error(session_id: str):
    await update_session(session_id, status=ERROR)


async def mark_execution_done(session_id: str):
    await update_session(session_id, status=DONE)

