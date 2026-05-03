# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, Form, HTTPException, Request

from backend.admin_auth import current_user_required
from backend.analysis import METHOD_CATEGORIES, METHOD_META, build_execute_params
from backend.analysis.common import build_slot_param_example
from backend.config import (
    AI_INTERPRET_RATE_LIMIT_COUNT,
    AI_INTERPRET_RATE_LIMIT_WINDOW_SECONDS,
    AI_PLAN_RATE_LIMIT_COUNT,
    AI_PLAN_RATE_LIMIT_WINDOW_SECONDS,
)
from backend.runtime_control import client_ip, enforce_rate_limit
from backend.services.analysis_service import (
    delete_analysis_result_for_session,
    download_word_report_for_session,
    get_analysis_results_for_session,
    rename_analysis_result_for_session,
)
from backend.services.session_access import get_session_or_404
from backend.services.job_service import (
    stream_execute_plan_job_events,
    submit_ai_interpret_job,
    submit_ai_plan_job,
    submit_execute_method_job,
    submit_execute_plan_job,
    submit_generate_report_job,
)

router = APIRouter()


@router.post("/api/plan/{session_id}")
async def create_plan(session_id: str, request: Request, research_topic: str = Form(""), variable_desc: str = Form(""), hypotheses: str = Form(""), analysis_request: str = Form(""), user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    await enforce_rate_limit(
        "ai-plan",
        f"user:{user['id']}:{client_ip(request)}",
        limit=AI_PLAN_RATE_LIMIT_COUNT,
        window_seconds=AI_PLAN_RATE_LIMIT_WINDOW_SECONDS,
        message="AI 规划请求过于频繁，请稍后重试",
    )
    return await submit_ai_plan_job(
        session_id,
        user,
        research_topic,
        variable_desc,
        hypotheses,
        analysis_request,
    )


@router.post("/api/execute/{session_id}")
async def execute_plan(session_id: str, plan_edit: str = Form(None), user=Depends(current_user_required)):
    return await submit_execute_plan_job(session_id, user, plan_edit)


@router.post("/api/execute-stream/{session_id}")
async def execute_plan_stream(session_id: str, plan_edit: str = Form(None), user=Depends(current_user_required)):
    return await stream_execute_plan_job_events(session_id, user, plan_edit)


@router.get("/api/results/{session_id}")
async def get_analysis_results(session_id: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await get_analysis_results_for_session(session_id, user)


@router.patch("/api/results/{session_id}/{result_id}")
async def rename_analysis_result(session_id: str, result_id: int, body: dict = None, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await rename_analysis_result_for_session(session_id, result_id, body)


@router.delete("/api/results/{session_id}/{result_id}")
async def delete_analysis_result(session_id: str, result_id: int, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await delete_analysis_result_for_session(session_id, result_id)


@router.get("/api/download/{session_id}")
async def download_word(session_id: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await download_word_report_for_session(session_id)


@router.post("/api/download/{session_id}")
async def generate_word_report(session_id: str, user=Depends(current_user_required)):
    return await submit_generate_report_job(session_id, user)


@router.get("/api/methods")
async def list_methods():
    return {"methods": METHOD_META, "categories": METHOD_CATEGORIES}


@router.get("/api/methods/{method_key}")
async def get_method_detail(method_key: str):
    meta = METHOD_META.get(method_key)
    if not meta:
        raise HTTPException(404, "分析方法不存在")
    slot_params_example = build_slot_param_example(meta)
    return {
        "method": method_key,
        "meta": meta,
        "slot_params_example": slot_params_example,
        "execute_params_example": build_execute_params(method_key, slot_params_example),
    }


@router.post("/api/execute-method/{session_id}")
async def execute_method(session_id: str, body: dict = None, user=Depends(current_user_required)):
    body = body or {}
    return await submit_execute_method_job(session_id, user, body.get("method", ""), body.get("params", {}))


@router.post("/api/ai-interpret")
async def ai_interpret(request: Request, body: dict = None, user=Depends(current_user_required)):
    await enforce_rate_limit(
        "ai-interpret",
        f"user:{user['id']}:{client_ip(request)}",
        limit=AI_INTERPRET_RATE_LIMIT_COUNT,
        window_seconds=AI_INTERPRET_RATE_LIMIT_WINDOW_SECONDS,
        message="AI 解读请求过于频繁，请稍后重试",
    )
    return await submit_ai_interpret_job(user, body)

