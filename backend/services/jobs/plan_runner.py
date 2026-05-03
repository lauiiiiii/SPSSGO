# -*- coding: utf-8 -*-
"""计划任务执行支撑，只管 execute_plan 作业编排细节，别把通用 job 生命周期塞进来。"""
from __future__ import annotations

import asyncio
import json

import pandas as pd

from backend.database import delete_results_for_job, update_job, update_session
from backend.domain import DONE, EXECUTING, normalize_analysis_items
from backend.file_parser import build_data_context
from backend.services.execution_support import execute_generated_custom_code, generate_analysis_tasks, run_generated_analysis_code
from backend.services.jobs.common import job_progress, json_loads
from backend.template_executor import execute_template_tasks


def build_plan_execution_context(session: dict, version: dict, plan: str) -> dict:
    return {
        "plan": plan,
        "summary": version.get("summary") or json_loads(session.get("data_summary"), {}),
        "data_context": build_data_context(
            version.get("summary") or json_loads(session.get("data_summary"), {}),
            session.get("questionnaire_text") or "",
        ),
        "research_info": (
            f"研究主题: {session.get('research_topic') or ''}\n"
            f"变量说明: {session.get('variable_desc') or ''}\n"
            f"研究假设: {session.get('hypotheses') or ''}\n"
        ),
    }


async def try_run_template_plan_job(
    job: dict,
    context: dict,
    filepath: str,
    dataset_version_id: int,
    save_results,
):
    try:
        tasks = await generate_analysis_tasks(context["data_context"], context["plan"], context["research_info"])
        await update_job(job["id"], progress=job_progress("template", "已生成任务配置，正在执行结构化分析", total=len(tasks)))
        custom_tasks = [task for task in tasks if task.get("method") == "custom"]
        template_tasks = [task for task in tasks if task.get("method") != "custom"]
        if not template_tasks:
            return None

        template_df = await asyncio.to_thread(pd.read_parquet, filepath)
        template_result = await asyncio.to_thread(execute_template_tasks, template_df, template_tasks)
        if not template_result["success"]:
            return None

        await delete_results_for_job(job["id"])
        all_results = normalize_analysis_items(template_result["results"])
        task_code = json.dumps(tasks, ensure_ascii=False, indent=2)
        await save_results(job, all_results, task_code, dataset_version_id)
        if custom_tasks:
            try:
                await update_job(job["id"], progress=job_progress("sandbox", "正在沙箱中执行 AI 自定义代码", custom_tasks=len(custom_tasks)))
                code_result, code = await execute_generated_custom_code(
                    context["data_context"],
                    context["research_info"],
                    "\n".join([task.get("custom_desc", "") for task in custom_tasks]),
                    filepath,
                    storage_category="datasets",
                    session_id=job["session_id"],
                    storage_key=context["storage_key"],
                    owner_id=job["owner_id"],
                    dataset_version_id=dataset_version_id,
                    parent_job_id=job["id"],
                )
                if code_result["success"]:
                    custom_items = normalize_analysis_items(code_result["results"])
                    await save_results(job, custom_items, code, dataset_version_id)
                    all_results.extend(custom_items)
            except Exception:
                pass
        await update_session(job["session_id"], status=DONE)
        return {"success": True, "count": len(all_results), "mode": "template", "dataset_version_id": dataset_version_id}
    except Exception:
        return None


async def run_generated_plan_job(
    job: dict,
    context: dict,
    filepath: str,
    dataset_version_id: int,
    save_results,
):
    await update_job(job["id"], progress=job_progress("fallback", "切换到 AI 代码生成模式"))
    last_error = ""
    last_code = ""
    for attempt in range(3):
        try:
            await update_job(
                job["id"],
                progress=job_progress(
                    "generating_code",
                    "AI 正在生成分析代码" if attempt == 0 else f"第 {attempt + 1} 次重试，AI 正在修复代码",
                    attempt=attempt + 1,
                ),
            )
            await update_job(job["id"], progress=job_progress("sandbox", "正在沙箱中执行 AI 代码", attempt=attempt + 1))
            exec_result, code = await run_generated_analysis_code(
                context["data_context"],
                context["plan"],
                context["research_info"],
                filepath,
                last_error,
                storage_category="datasets",
                session_id=job["session_id"],
                storage_key=context["storage_key"],
                owner_id=job["owner_id"],
                dataset_version_id=dataset_version_id,
                parent_job_id=job["id"],
                stage="fallback",
                attempt=attempt + 1,
            )
            last_code = code
            if exec_result["success"]:
                await delete_results_for_job(job["id"])
                items = normalize_analysis_items(exec_result["results"])
                await save_results(job, items, code, dataset_version_id)
                await update_session(job["session_id"], status=DONE)
                return {"success": True, "count": len(items), "mode": "code_generation", "dataset_version_id": dataset_version_id}
            last_error = exec_result["error"]
        except Exception as exc:
            last_error = str(exc)
    raise RuntimeError(f"代码执行失败（已重试3次）: {last_error or last_code or '未知错误'}")
