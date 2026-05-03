# -*- coding: utf-8 -*-
"""分享路由，只负责收发分享请求，别把快照校验和存储细节塞进来。"""
from fastapi import APIRouter, Depends

from backend.admin_auth import current_user_required
from backend.services.shared_report_service import (
    access_public_shared_report,
    create_shared_report_snapshot,
    get_public_shared_report,
)

router = APIRouter()


@router.post("/api/shared-reports")
async def create_shared_report(body: dict | None = None, user=Depends(current_user_required)):
    return await create_shared_report_snapshot(body, user)


@router.get("/api/shared-reports/{share_token}")
async def get_shared_report(share_token: str):
    return await get_public_shared_report(share_token)


@router.post("/api/shared-reports/{share_token}/access")
async def access_shared_report(share_token: str, body: dict | None = None):
    return await access_public_shared_report(share_token, body)
