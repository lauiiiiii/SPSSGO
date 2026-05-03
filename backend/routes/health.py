# -*- coding: utf-8 -*-
"""健康检查 API 入口，只做协议层转发，别把基础设施探测细节塞进来。"""
from fastapi import APIRouter

from backend.observability import metrics_response
from backend.services.health_service import get_liveness_payload, get_readiness_response

router = APIRouter()


@router.get("/api/health")
async def health_live():
    return await get_liveness_payload()


@router.get("/api/health/ready")
async def health_ready():
    return await get_readiness_response()


@router.get("/metrics", include_in_schema=False)
async def metrics():
    return metrics_response()
