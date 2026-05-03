# -*- coding: utf-8 -*-
"""分析执行编排，只管计划执行流程，别把结果管理和报告下载塞进来。"""
import json

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from backend.analysis import METHOD_REGISTRY
from backend.database import get_session, update_session
from backend.domain import EXECUTING, normalize_analysis_items
from backend.file_parser import build_data_context
from backend.services.execution_support import (
    execute_generated_custom_code,
    generate_analysis_tasks,
    mark_execution_done,
    mark_execution_error,
    run_generated_analysis_code,
    save_analysis_items,
)
from backend.services.file_service import find_data_file_name, load_dataframe, materialized_upload
from backend.template_executor import execute_template_tasks


async def prepare_plan_execution(session_id: str, plan_edit: str | None) -> dict:
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    plan = plan_edit if plan_edit else session["plan"]
    if not plan:
        raise HTTPException(400, "没有分析计划")

    await update_session(session_id, plan=plan, plan_confirmed=1, status=EXECUTING)
    data_summary = json.loads(session["data_summary"]) if session["data_summary"] else {}
    return {
        "session": session,
        "session_id": session_id,
        "plan": plan,
        "data_context": build_data_context(data_summary, session["questionnaire_text"] or ""),
        "research_info": (
            f"研究主题: {session['research_topic']}\n"
            f"变量说明: {session['variable_desc']}\n"
            f"研究假设: {session['hypotheses']}\n"
        ),
        "data_file_name": find_data_file_name(session_id),
    }


async def execute_plan_with_context(context: dict):
    session_id = context["session_id"]
    data_file_name = context["data_file_name"]
    if not data_file_name:
        raise HTTPException(400, "找不到数据文件")

    with materialized_upload(session_id, data_file_name) as data_file:
        template_response = await _run_template_execution(context, data_file)
        if template_response is not None:
            return template_response
        return await _run_generated_execution(context, data_file)


async def stream_plan_execution_with_context(context: dict):
    async def event_stream():
        if not context["data_file_name"]:
            yield _sse("error", {"message": "找不到数据文件"})
            await mark_execution_error(context["session_id"])
            return

        yield _sse("progress", {"stage": "generating_tasks", "message": "AI 正在解析分析计划，生成任务配置..."})
        streamed = await _stream_template_execution(context)
        if streamed is not None:
            async for payload in streamed:
                yield payload
            return

        async for payload in _stream_generated_execution(context):
            yield payload

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _run_template_execution(context: dict, data_file: str):
    try:
        tasks = await generate_analysis_tasks(context["data_context"], context["plan"], context["research_info"])
        custom_tasks = [t for t in tasks if t.get("method") == "custom"]
        template_tasks = [t for t in tasks if t.get("method") != "custom"]
        if not template_tasks:
            return None
        template_result = execute_template_tasks(load_dataframe(data_file), template_tasks)
        if not template_result["success"]:
            return None

        all_results = normalize_analysis_items(template_result["results"])
        if custom_tasks:
            try:
                code_result, _ = await execute_generated_custom_code(
                    context["data_context"],
                    context["research_info"],
                    "\n".join([t.get("custom_desc", "") for t in custom_tasks]),
                    data_file,
                )
                if code_result["success"]:
                    all_results.extend(normalize_analysis_items(code_result["results"]))
            except Exception:
                pass
        await save_analysis_items(context["session_id"], all_results, "[模板引擎]")
        await mark_execution_done(context["session_id"])
        return {
            "success": True,
            "results": all_results,
            "code": json.dumps(tasks, ensure_ascii=False, indent=2),
            "mode": "template",
        }
    except Exception:
        return None


async def _run_generated_execution(context: dict, data_file: str):
    last_error = ""
    for attempt in range(3):
        try:
            exec_result, code = await run_generated_analysis_code(
                context["data_context"],
                context["plan"],
                context["research_info"],
                data_file,
                last_error,
            )
            if exec_result["success"]:
                items = normalize_analysis_items(exec_result["results"])
                await save_analysis_items(context["session_id"], items, code)
                await mark_execution_done(context["session_id"])
                return {"success": True, "results": items, "code": code, "mode": "code_generation"}
            last_error = exec_result["error"]
            if attempt == 2:
                await mark_execution_error(context["session_id"])
                return {"success": False, "error": f"代码执行失败（已重试3次）: {last_error}", "code": code}
        except Exception as exc:
            last_error = str(exc)
            if attempt == 2:
                await mark_execution_error(context["session_id"])
                return {"success": False, "error": f"执行异常: {last_error}"}


async def _stream_template_execution(context: dict):
    try:
        tasks = await generate_analysis_tasks(context["data_context"], context["plan"], context["research_info"])
        custom_tasks = [t for t in tasks if t.get("method") == "custom"]
        template_tasks = [t for t in tasks if t.get("method") != "custom"]
        if not template_tasks:
            return None

        async def generator():
            total = len(template_tasks)
            yield _sse("progress", {"stage": "executing_templates", "message": f"开始执行 {total} 项分析...", "current": 0, "total": total})
            with materialized_upload(context["session_id"], context["data_file_name"]) as data_file:
                df = load_dataframe(data_file)
                all_results = []
                for i, task in enumerate(template_tasks):
                    func = METHOD_REGISTRY.get(task.get("method", ""))
                    if func is None:
                        continue
                    try:
                        items = normalize_analysis_items(func(df, task))
                        for item in items:
                            all_results.append(item)
                            await save_analysis_items(context["session_id"], [item], "[模板引擎]")
                            yield _sse("result", item)
                    except Exception:
                        continue
                    yield _sse("progress", {"stage": "executing_templates", "message": f"已完成 {i + 1}/{total} 项分析", "current": i + 1, "total": total})

                if custom_tasks and all_results:
                    try:
                        code_result, code = await execute_generated_custom_code(
                            context["data_context"],
                            context["research_info"],
                            "\n".join([t.get("custom_desc", "") for t in custom_tasks]),
                            data_file,
                        )
                        if code_result["success"]:
                            for item in normalize_analysis_items(code_result["results"]):
                                all_results.append(item)
                                await save_analysis_items(context["session_id"], [item], code)
                                yield _sse("result", item)
                    except Exception:
                        pass

            if all_results:
                await mark_execution_done(context["session_id"])
                yield _sse("done", {"success": True, "mode": "template", "total": len(all_results)})
                return

            async for payload in _stream_generated_execution(context):
                yield payload

        return generator()
    except Exception:
        return None


async def _stream_generated_execution(context: dict):
    yield _sse("progress", {"stage": "code_fallback", "message": "切换到 AI 代码生成模式..."})
    last_error = ""
    for attempt in range(3):
        try:
            yield _sse("progress", {"stage": "generating_code", "message": "AI 正在生成分析代码..." if attempt == 0 else f"第 {attempt + 1} 次重试，AI 正在修复代码..."})
            with materialized_upload(context["session_id"], context["data_file_name"]) as data_file:
                exec_result, code = await run_generated_analysis_code(
                    context["data_context"],
                    context["plan"],
                    context["research_info"],
                    data_file,
                    last_error,
                )
            yield _sse("progress", {"stage": "executing_code", "message": "正在执行分析代码..."})
            if exec_result["success"]:
                items = normalize_analysis_items(exec_result["results"])
                for item in items:
                    await save_analysis_items(context["session_id"], [item], code)
                    yield _sse("result", item)
                await mark_execution_done(context["session_id"])
                yield _sse("done", {"success": True, "mode": "code_generation", "total": len(items)})
                return
            last_error = exec_result["error"]
            if attempt == 2:
                await mark_execution_error(context["session_id"])
                yield _sse("error", {"message": f"代码执行失败（已重试3次）: {last_error}"})
        except Exception as exc:
            last_error = str(exc)
            if attempt == 2:
                await mark_execution_error(context["session_id"])
                yield _sse("error", {"message": f"执行异常: {last_error}"})


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
