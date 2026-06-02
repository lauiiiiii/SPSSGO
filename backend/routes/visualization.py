# -*- coding: utf-8 -*-
"""可视化绘图 API 入口，只做鉴权和转发，别保存图表配置。"""
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.admin_auth import current_user_required
from backend.services.session_access import get_session_or_404
from backend.services.session_data_service import allow_legacy_upload_reads
from backend.services.visualization_service import preview_visualization

router = APIRouter()


class VisualizationPreviewRequest(BaseModel):
    chart_type: str
    variables: dict[str, str | None] = Field(default_factory=dict)
    options: dict[str, Any] = Field(default_factory=dict)


@router.post("/api/visualizations/{session_id}/preview")
async def visualization_preview(session_id: str, req: VisualizationPreviewRequest, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    payload = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    return await preview_visualization(
        session_id,
        payload,
        allow_legacy_fallback=allow_legacy_upload_reads(user),
    )
