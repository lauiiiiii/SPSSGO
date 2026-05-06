# -*- coding: utf-8 -*-
"""数据集业务门面，只聚合数据集列表信息，别把上传解析和分析执行塞进来。"""

from fastapi import HTTPException

from backend.repositories.dataset_repository import (
    count_datasets_for_owner,
    copy_dataset_version,
    delete_dataset_version,
    get_dataset,
    get_dataset_for_session,
    get_dataset_version,
    list_datasets_for_owner,
    touch_dataset,
    update_dataset,
    update_dataset_version,
)
from backend.repositories.session_repository import delete_session
from backend.services.session_access import is_admin_user


def _extract_count(summary: dict, *keys: str) -> int:
    for key in keys:
        value = summary.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
    return 0


def _human_file_size(size_bytes: int | None) -> str:
    if not size_bytes:
        return ""
    units = ["B", "KB", "MB", "GB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.1f}".rstrip("0").rstrip(".") + f" {unit}"
        size /= 1024
    return f"{size:.1f} GB"


DATASET_SORT_KEYS = {"recent", "created", "name", "versions", "results"}
MAX_DATASET_PAGE_SIZE = 500


def _clean_page(page: int) -> int:
    return max(1, int(page or 1))


def _clean_page_size(page_size: int) -> int:
    return min(MAX_DATASET_PAGE_SIZE, max(1, int(page_size or MAX_DATASET_PAGE_SIZE)))


async def list_datasets_for_user(
    user: dict,
    *,
    q: str = "",
    sort: str = "recent",
    page: int = 1,
    page_size: int = MAX_DATASET_PAGE_SIZE,
    in_folder: int | None = None,
) -> dict:
    next_page = _clean_page(page)
    next_page_size = _clean_page_size(page_size)
    next_sort = sort if sort in DATASET_SORT_KEYS else "recent"
    query = (q or "").strip()
    admin = is_admin_user(user)
    offset = (next_page - 1) * next_page_size

    rows = await list_datasets_for_owner(
        user["id"],
        is_admin=admin,
        limit=next_page_size,
        offset=offset,
        query=query,
        sort=next_sort,
        in_folder=in_folder,
    )
    total = await count_datasets_for_owner(user["id"], is_admin=admin, query=query, in_folder=in_folder)
    datasets = []
    for row in rows:
        summary = row.get("current_summary") or {}
        display_name = row.get("name") or row.get("research_topic") or row.get("original_filename") or f"数据集 {row['id']}"
        datasets.append(
            {
                "id": row["id"],
                "session_id": row["session_id"],
                "name": display_name,
                "original_filename": row.get("original_filename") or "",
                "created_at": row.get("created_at"),
                "last_used_at": row.get("last_used_at") or row.get("created_at"),
                "status": row.get("session_status") or "",
                "current_version_id": row.get("current_version_id") or row.get("current_dataset_version_id"),
                "current_version_no": row.get("current_version_no"),
                "version_count": int(row.get("version_count") or 0),
                "result_count": int(row.get("result_count") or 0),
                "row_count": _extract_count(summary, "total_rows", "row_count"),
                "column_count": _extract_count(summary, "total_cols", "column_count"),
                "file_size": _human_file_size(row.get("size_bytes")),
                "folder_id": row.get("folder_id"),
                "summary": summary,
            }
        )
    return {
        "datasets": datasets,
        "total": total,
        "page": next_page,
        "page_size": next_page_size,
        "sort": next_sort,
        "q": query,
    }


async def rename_dataset_version_for_user(version_id: int, name: str, user: dict) -> dict:
    next_name = (name or "").strip()
    if not next_name:
        raise HTTPException(400, "版本名称不能为空")
    if len(next_name) > 120:
        raise HTTPException(400, "版本名称不能超过 120 个字符")

    version = await get_dataset_version(version_id)
    if not version or (not is_admin_user(user) and version.get("owner_id") != user["id"]):
        raise HTTPException(404, "版本不存在")

    await update_dataset_version(version_id, name=next_name)
    return {"id": version_id, "name": next_name}


async def delete_dataset_version_for_user(version_id: int, user: dict) -> dict:
    version = await get_dataset_version(version_id)
    if not version or (not is_admin_user(user) and version.get("owner_id") != user["id"]):
        raise HTTPException(404, "版本不存在")

    dataset = await get_dataset(version.get("dataset_id"))
    if not dataset or (not is_admin_user(user) and dataset.get("owner_id") != user["id"]):
        raise HTTPException(404, "数据集不存在")
    if str(dataset.get("current_version_id")) == str(version_id):
        raise HTTPException(400, "当前使用中的版本不能删除，请先切换到其他版本")

    result = await delete_dataset_version(version_id)
    return {
        "ok": True,
        "id": version_id,
        "dataset_id": version.get("dataset_id"),
        "deleted_results": result.get("deleted_results", 0),
    }


async def copy_dataset_version_for_user(version_id: int, name: str | None, user: dict) -> dict:
    version = await get_dataset_version(version_id)
    if not version or (not is_admin_user(user) and version.get("owner_id") != user["id"]):
        raise HTTPException(404, "版本不存在")

    next_name = (name or "").strip()
    if not next_name:
        raise HTTPException(400, "版本名称不能为空")
    if len(next_name) > 120:
        raise HTTPException(400, "版本名称不能超过 120 个字符")
    next_version = await copy_dataset_version(version_id, next_name)
    if not next_version:
        raise HTTPException(404, "版本不存在")
    return {
        "success": True,
        "message": f"已复制为数据版本 v{next_version['version_no']}",
        "dataset_version_id": next_version["id"],
        "dataset_version_no": next_version["version_no"],
    }


async def rename_dataset_for_user(dataset_id: int, name: str, user: dict) -> dict:
    next_name = (name or "").strip()
    if not next_name:
        raise HTTPException(400, "数据集名称不能为空")
    if len(next_name) > 120:
        raise HTTPException(400, "数据集名称不能超过 120 个字符")

    dataset = await get_dataset(dataset_id)
    if not dataset or (not is_admin_user(user) and dataset.get("owner_id") != user["id"]):
        raise HTTPException(404, "数据集不存在")

    await update_dataset(dataset_id, name=next_name)
    return {
        "id": dataset_id,
        "session_id": dataset["session_id"],
        "name": next_name,
    }


async def touch_dataset_for_user(dataset_id: int, user: dict) -> dict:
    dataset = await get_dataset(dataset_id)
    if not dataset or (not is_admin_user(user) and dataset.get("owner_id") != user["id"]):
        raise HTTPException(404, "数据集不存在")
    await touch_dataset(dataset_id)
    return {"ok": True, "id": dataset_id}


async def delete_dataset_for_user(dataset_id: int, user: dict) -> dict:
    dataset = await get_dataset(dataset_id)
    if not dataset or (not is_admin_user(user) and dataset.get("owner_id") != user["id"]):
        raise HTTPException(404, "数据集不存在")
    await delete_session(dataset["session_id"])
    return {"ok": True, "id": dataset_id, "session_id": dataset["session_id"]}


async def batch_delete_datasets_for_user(session_ids: list[str], user: dict) -> dict:
    if not session_ids:
        raise HTTPException(400, "未指定要删除的数据集")
    if len(session_ids) > 500:
        raise HTTPException(400, "一次最多删除 500 个数据集")

    deleted = []
    failed = []
    for session_id in session_ids:
        dataset = await get_dataset_for_session(session_id)
        if not dataset or (not is_admin_user(user) and dataset.get("owner_id") != user["id"]):
            failed.append({"session_id": session_id, "reason": "数据集不存在或无权限"})
            continue
        try:
            await delete_session(dataset["session_id"])
            deleted.append(session_id)
        except Exception as exc:
            failed.append({"session_id": session_id, "reason": str(exc)})

    return {"deleted": deleted, "failed": failed, "count": len(deleted)}
