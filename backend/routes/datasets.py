# -*- coding: utf-8 -*-
"""数据集 API 入口，只做鉴权和转发，具体聚合放 service。"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.admin_auth import current_user_required
from backend.services.dataset_folder_service import (
    batch_move_datasets_to_folder_for_user,
    create_dataset_folder_for_user,
    delete_dataset_folder_for_user,
    list_dataset_folders_for_user,
    move_dataset_to_folder_for_user,
    rename_dataset_folder_for_user,
)
from backend.services.dataset_service import (
    batch_delete_datasets_for_user,
    copy_dataset_version_for_user,
    delete_dataset_for_user,
    delete_dataset_version_for_user,
    list_datasets_for_user,
    rename_dataset_for_user,
    rename_dataset_version_for_user,
    touch_dataset_for_user,
)

router = APIRouter()


class RenameDatasetRequest(BaseModel):
    name: str


class CopyDatasetVersionRequest(BaseModel):
    name: str | None = None


class FolderRequest(BaseModel):
    name: str


class MoveDatasetFolderRequest(BaseModel):
    session_id: str
    folder_id: int | None = None


class BatchDeleteDatasetsRequest(BaseModel):
    session_ids: list[str]


class BatchMoveDatasetsRequest(BaseModel):
    session_ids: list[str]
    folder_id: int | None = None


@router.get("/api/datasets")
async def list_datasets(
    q: str = "",
    sort: str = "recent",
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
    in_folder: int | None = Query(None, ge=0, le=1),
    user=Depends(current_user_required),
):
    return await list_datasets_for_user(user, q=q, sort=sort, page=page, page_size=page_size, in_folder=in_folder)


@router.patch("/api/datasets/{dataset_id}")
async def rename_dataset(dataset_id: int, req: RenameDatasetRequest, user=Depends(current_user_required)):
    return await rename_dataset_for_user(dataset_id, req.name, user)


@router.patch("/api/dataset-versions/{version_id}")
async def rename_dataset_version(version_id: int, req: RenameDatasetRequest, user=Depends(current_user_required)):
    return await rename_dataset_version_for_user(version_id, req.name, user)


@router.delete("/api/dataset-versions/{version_id}")
async def delete_dataset_version(version_id: int, user=Depends(current_user_required)):
    return await delete_dataset_version_for_user(version_id, user)


@router.post("/api/dataset-versions/{version_id}/copy")
async def copy_dataset_version(version_id: int, req: CopyDatasetVersionRequest, user=Depends(current_user_required)):
    return await copy_dataset_version_for_user(version_id, req.name, user)


@router.post("/api/datasets/{dataset_id}/touch")
async def touch_dataset(dataset_id: int, user=Depends(current_user_required)):
    return await touch_dataset_for_user(dataset_id, user)


@router.delete("/api/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int, user=Depends(current_user_required)):
    return await delete_dataset_for_user(dataset_id, user)


@router.get("/api/dataset-folders")
async def list_dataset_folders(user=Depends(current_user_required)):
    return await list_dataset_folders_for_user(user)


@router.post("/api/dataset-folders")
async def create_dataset_folder(req: FolderRequest, user=Depends(current_user_required)):
    return await create_dataset_folder_for_user(req.name, user)


@router.patch("/api/dataset-folders/{folder_id}")
async def rename_dataset_folder(folder_id: int, req: FolderRequest, user=Depends(current_user_required)):
    return await rename_dataset_folder_for_user(folder_id, req.name, user)


@router.delete("/api/dataset-folders/{folder_id}")
async def delete_dataset_folder(folder_id: int, user=Depends(current_user_required)):
    return await delete_dataset_folder_for_user(folder_id, user)


@router.put("/api/dataset-folder-items")
async def move_dataset_folder_item(req: MoveDatasetFolderRequest, user=Depends(current_user_required)):
    return await move_dataset_to_folder_for_user(req.session_id, req.folder_id, user)


@router.post("/api/datasets/batch-delete")
async def batch_delete_datasets(req: BatchDeleteDatasetsRequest, user=Depends(current_user_required)):
    return await batch_delete_datasets_for_user(req.session_ids, user)


@router.post("/api/dataset-folder-items/batch-move")
async def batch_move_dataset_folder_items(req: BatchMoveDatasetsRequest, user=Depends(current_user_required)):
    return await batch_move_datasets_to_folder_for_user(req.session_ids, req.folder_id, user)
