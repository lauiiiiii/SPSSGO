# -*- coding: utf-8 -*-
"""数据集文件夹业务层，只处理权限和命名规则，别碰文件存储。"""
from fastapi import HTTPException

from backend.repositories.dataset_folder_repository import (
    create_folder,
    delete_folder,
    get_folder,
    get_folder_by_owner_name,
    list_folders_for_owner,
    rename_folder,
    set_dataset_folder,
)
from backend.repositories.dataset_repository import get_dataset_for_session
from backend.services.session_access import is_admin_user


def _clean_folder_name(name: str) -> str:
    next_name = (name or "").strip()
    if not next_name:
        raise HTTPException(400, "文件夹名称不能为空")
    if len(next_name) > 80:
        raise HTTPException(400, "文件夹名称不能超过 80 个字符")
    return next_name


async def list_dataset_folders_for_user(user: dict) -> dict:
    return {"folders": await list_folders_for_owner(user["id"])}


async def create_dataset_folder_for_user(name: str, user: dict) -> dict:
    next_name = _clean_folder_name(name)
    await _ensure_folder_name_available(user["id"], next_name)
    folder = await create_folder(user["id"], next_name)
    return {"folder": folder}


async def rename_dataset_folder_for_user(folder_id: int, name: str, user: dict) -> dict:
    folder = await _get_folder_for_user(folder_id, user)
    next_name = _clean_folder_name(name)
    await _ensure_folder_name_available(folder["owner_id"], next_name, ignore_folder_id=folder["id"])
    await rename_folder(folder["id"], next_name)
    folder["name"] = next_name
    return {"folder": _shape_folder(folder)}


async def delete_dataset_folder_for_user(folder_id: int, user: dict) -> dict:
    folder = await _get_folder_for_user(folder_id, user)
    await delete_folder(folder["id"])
    return {"ok": True}


async def move_dataset_to_folder_for_user(session_id: str, folder_id: int | None, user: dict) -> dict:
    dataset = await get_dataset_for_session(session_id)
    if not dataset or (not is_admin_user(user) and dataset.get("owner_id") != user["id"]):
        raise HTTPException(404, "数据集不存在")

    target_folder_id = None
    if folder_id:
        folder = await _get_folder_for_user(folder_id, user)
        target_folder_id = folder["id"]

    await set_dataset_folder(dataset["id"], target_folder_id)
    return {"ok": True, "session_id": session_id, "folder_id": target_folder_id}


async def batch_move_datasets_to_folder_for_user(session_ids: list[str], folder_id: int | None, user: dict) -> dict:
    if not session_ids:
        raise HTTPException(400, "未指定要移动的数据集")
    if len(session_ids) > 500:
        raise HTTPException(400, "一次最多移动 500 个数据集")

    target_folder_id = None
    if folder_id:
        folder = await _get_folder_for_user(folder_id, user)
        target_folder_id = folder["id"]

    moved = []
    failed = []
    for session_id in session_ids:
        dataset = await get_dataset_for_session(session_id)
        if not dataset or (not is_admin_user(user) and dataset.get("owner_id") != user["id"]):
            failed.append({"session_id": session_id, "reason": "数据集不存在或无权限"})
            continue
        try:
            await set_dataset_folder(dataset["id"], target_folder_id)
            moved.append(session_id)
        except Exception as exc:
            failed.append({"session_id": session_id, "reason": str(exc)})

    return {"moved": moved, "failed": failed, "folder_id": target_folder_id, "count": len(moved)}


async def _get_folder_for_user(folder_id: int, user: dict) -> dict:
    folder = await get_folder(folder_id)
    if not folder or (not is_admin_user(user) and folder.get("owner_id") != user["id"]):
        raise HTTPException(404, "文件夹不存在")
    return folder


async def _ensure_folder_name_available(owner_id: int, name: str, *, ignore_folder_id: int | None = None) -> None:
    existing = await get_folder_by_owner_name(owner_id, name)
    if existing and existing.get("id") != ignore_folder_id:
        raise HTTPException(400, "同名文件夹已存在")


def _shape_folder(folder: dict) -> dict:
    return {
        "id": folder["id"],
        "name": folder.get("name") or "",
        "created_at": folder.get("created_at"),
        "sessionIds": folder.get("sessionIds") or [],
    }
