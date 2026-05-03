# -*- coding: utf-8 -*-
import os

import pandas as pd
from fastapi import HTTPException

from backend.config import SESSION_WRITE_LOCK_TTL_SECONDS
from backend.database import (
    delete_variable_metadata,
    get_variable_metadata_map,
    rename_variable_metadata,
    upsert_variable_metadata,
)
from backend.file_parser import parse_data_file
from backend.processing import run_process_method
from backend.runtime_control import session_write_lock
from backend.services.dataset_version_service import (
    activate_dataset_version,
    create_dataset_version_from_dataframe,
    list_dataset_versions_for_session,
    save_current_metadata_snapshot,
)
from backend.services.session_data_service import allow_legacy_upload_reads, load_session_dataframe


def save_df(df, filepath: str):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".xlsx", ".xls"):
        df.to_excel(filepath, index=False)
    elif ext == ".csv":
        df.to_csv(filepath, index=False)
    elif ext in (".tsv", ".txt"):
        df.to_csv(filepath, index=False, sep="\t")
    elif ext == ".parquet":
        df.to_parquet(filepath, index=False)
    else:
        df.to_excel(filepath.rsplit(".", 1)[0] + ".xlsx", index=False)


def run_process(filepath: str, method: str, params: dict):
    df, _ = parse_data_file(filepath)
    try:
        df, msg = run_process_method(df, method, params)
    except ValueError as exc:
        return {"success": False, "error": str(exc)}
    save_df(df, filepath)
    return {"success": True, "message": msg}


async def rename_variable_for_session(session_id: str, column_name: str, new_name: str, user: dict):
    new_name = (new_name or "").strip()
    if not new_name:
        raise HTTPException(400, "新变量名不能为空")
    if new_name == column_name:
        return {"success": True, "message": "变量名未变更"}

    try:
        async with session_write_lock(
            session_id,
            holder=f"rename_variable:{user['id']}",
            ttl_seconds=SESSION_WRITE_LOCK_TTL_SECONDS,
            wait_timeout=1.5,
            busy_message="当前会话已有写任务正在执行，暂时无法重命名变量",
        ):
            df = await _load_writable_dataframe(session_id, user)
            if column_name not in df.columns:
                raise HTTPException(404, "变量不存在")
            if new_name in df.columns:
                raise HTTPException(400, "新变量名已存在")

            df = df.rename(columns={column_name: new_name})
            await rename_variable_metadata(session_id, column_name, new_name)
            next_version = await _create_version_from_dataframe(session_id, user["id"], df)

        return {
            "success": True,
            "message": f"已将变量 {column_name} 重命名为 {new_name}",
            "dataset_version_id": next_version["id"],
            "dataset_version_no": next_version["version_no"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"变量重命名失败: {str(exc)}")


async def change_variable_type_for_session(session_id: str, column_name: str, target_type: str, user: dict):
    target_type = (target_type or "").strip()
    if target_type not in {"categorical", "numeric"}:
        raise HTTPException(400, "目标变量类型不合法")

    try:
        async with session_write_lock(
            session_id,
            holder=f"change_variable_type:{user['id']}",
            ttl_seconds=SESSION_WRITE_LOCK_TTL_SECONDS,
            wait_timeout=1.5,
            busy_message="当前会话已有写任务正在执行，暂时无法修改变量类型",
        ):
            df = await _load_writable_dataframe(session_id, user)
            if column_name not in df.columns:
                raise HTTPException(404, "变量不存在")

            metadata_map = await get_variable_metadata_map(session_id)
            current_meta = metadata_map.get(column_name, {})
            await upsert_variable_metadata(
                session_id,
                column_name,
                var_type=target_type,
                display_name=current_meta.get("display_name"),
                value_labels={} if target_type == "numeric" else current_meta.get("value_labels"),
                code_rules=current_meta.get("code_rules"),
            )
            next_version = await _create_version_from_dataframe(session_id, user["id"], df)

        return {
            "success": True,
            "message": f"已将变量 {column_name} 转换为{'定类' if target_type == 'categorical' else '定量'}",
            "dataset_version_id": next_version["id"],
            "dataset_version_no": next_version["version_no"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"变量类型转换失败: {str(exc)}")


async def delete_variable_for_session(session_id: str, column_name: str, user: dict):
    try:
        async with session_write_lock(
            session_id,
            holder=f"delete_variable:{user['id']}",
            ttl_seconds=SESSION_WRITE_LOCK_TTL_SECONDS,
            wait_timeout=1.5,
            busy_message="当前会话已有写任务正在执行，暂时无法删除变量",
        ):
            df = await _load_writable_dataframe(session_id, user)
            if column_name not in df.columns:
                raise HTTPException(404, "变量不存在")

            df = df.drop(columns=[column_name])
            await delete_variable_metadata(session_id, column_name)
            next_version = await _create_version_from_dataframe(session_id, user["id"], df)

        return {
            "success": True,
            "message": f"已删除变量 {column_name}",
            "dataset_version_id": next_version["id"],
            "dataset_version_no": next_version["version_no"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"删除变量失败: {str(exc)}")


async def list_dataset_versions_payload(session_id: str, current_dataset_version_id: int | None):
    return {
        "current_dataset_version_id": current_dataset_version_id,
        "versions": await list_dataset_versions_for_session(session_id),
    }


async def activate_dataset_version_for_session(session_id: str, version_id: int, user: dict):
    try:
        async with session_write_lock(
            session_id,
            holder=f"activate_dataset_version:{user['id']}",
            ttl_seconds=SESSION_WRITE_LOCK_TTL_SECONDS,
            wait_timeout=1.5,
            busy_message="当前会话已有写任务正在执行，暂时无法切换数据版本",
        ):
            version = await activate_dataset_version(session_id, version_id)

        return {
            "success": True,
            "message": f"已切换到数据版本 v{version['version_no']}",
            "dataset_version_id": version["id"],
            "dataset_version_no": version["version_no"],
        }
    except RuntimeError as exc:
        raise HTTPException(404, str(exc))


async def _load_writable_dataframe(session_id: str, user: dict) -> pd.DataFrame:
    return await load_session_dataframe(
        session_id,
        allow_legacy_fallback=allow_legacy_upload_reads(user),
    )


async def _create_version_from_dataframe(session_id: str, owner_id: int, df: pd.DataFrame):
    version, _ = await create_dataset_version_from_dataframe(session_id, owner_id, df)
    await save_current_metadata_snapshot(session_id, version["storage_key"])
    return version

