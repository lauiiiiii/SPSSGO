# -*- coding: utf-8 -*-
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.admin_auth import current_user_required
from backend.services.session_access import get_session_or_404
from backend.services.job_service import submit_process_job
from backend.services.processing_service import (
    activate_dataset_version_for_session,
    change_variable_type_for_session,
    delete_variable_for_session,
    list_dataset_versions_payload,
    rename_variable_for_session,
)

router = APIRouter()


class ProcessRequest(BaseModel):
    method: str
    params: Dict[str, Any] = {}


class RenameVariableRequest(BaseModel):
    new_name: str


class ChangeVariableTypeRequest(BaseModel):
    target_type: str


class ActivateDatasetVersionRequest(BaseModel):
    version_id: int


@router.post("/api/process/{session_id}")
async def process_data(session_id: str, req: ProcessRequest, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await submit_process_job(session_id, user, req.method, req.params or {})


@router.patch("/api/variables/{session_id}/{column_name}/rename")
async def rename_variable(session_id: str, column_name: str, req: RenameVariableRequest, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await rename_variable_for_session(session_id, column_name, req.new_name, user)


@router.patch("/api/variables/{session_id}/{column_name}/type")
async def change_variable_type(session_id: str, column_name: str, req: ChangeVariableTypeRequest, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await change_variable_type_for_session(session_id, column_name, req.target_type, user)


@router.delete("/api/variables/{session_id}/{column_name}")
async def delete_variable(session_id: str, column_name: str, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await delete_variable_for_session(session_id, column_name, user)


@router.get("/api/dataset-versions/{session_id}")
async def get_dataset_versions(session_id: str, user=Depends(current_user_required)):
    session = await get_session_or_404(session_id, user)
    return await list_dataset_versions_payload(session_id, session.get("current_dataset_version_id"))


@router.post("/api/dataset-versions/{session_id}/activate")
async def activate_dataset_version_route(session_id: str, req: ActivateDatasetVersionRequest, user=Depends(current_user_required)):
    await get_session_or_404(session_id, user)
    return await activate_dataset_version_for_session(session_id, req.version_id, user)

