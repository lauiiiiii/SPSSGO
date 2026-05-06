# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json
import os
import time
import tempfile
import uuid

import pandas as pd

from backend.database import (
    create_dataset_version,
    get_dataset_for_session,
    get_dataset_version,
    get_session,
    get_variable_metadata_map,
    list_dataset_versions,
    replace_variable_metadata,
    update_dataset,
    update_session,
)
from backend.file_parser import summarize_dataframe
from backend.storage import storage_service


def _metadata_snapshot_path(storage_key: str) -> str:
    return f"meta/{storage_key}.metadata.json"


async def create_dataset_version_from_dataframe(
    session_id: str,
    owner_id: int,
    df: pd.DataFrame,
    *,
    source_job_id: str | None = None,
):
    dataset = await get_dataset_for_session(session_id)
    if not dataset:
        raise RuntimeError("当前会话缺少数据集")

    content, summary = await asyncio.to_thread(_build_dataset_version_artifacts, df)

    storage_key = f"{uuid.uuid4().hex}.parquet"
    await asyncio.to_thread(storage_service.save_bytes, "datasets", session_id, storage_key, content)
    version = await create_dataset_version(
        dataset["id"],
        owner_id,
        session_id,
        storage_key,
        source_job_id=source_job_id,
        summary=summary,
        preview_rows=summary.get("preview_rows", []),
        schema=summary.get("columns", []),
    )
    return version, summary


async def save_current_metadata_snapshot(session_id: str, storage_key: str):
    metadata_map = await get_variable_metadata_map(session_id)
    await asyncio.to_thread(
        storage_service.save_text,
        "datasets",
        session_id,
        _metadata_snapshot_path(storage_key),
        json.dumps(metadata_map, ensure_ascii=False),
    )


async def load_metadata_snapshot(session_id: str, storage_key: str) -> dict | None:
    path = _metadata_snapshot_path(storage_key)
    if not await asyncio.to_thread(storage_service.exists, "datasets", session_id, path):
        return None
    try:
        payload = await asyncio.to_thread(storage_service.read_text, "datasets", session_id, path)
        return json.loads(payload)
    except Exception:
        return None


async def list_dataset_versions_for_session(session_id: str):
    session = await get_session(session_id)
    if not session or not session.get("current_dataset_id"):
        return []
    versions = await list_dataset_versions(session["current_dataset_id"])
    current_version_id = session.get("current_dataset_version_id")
    return [
        {
            **version,
            "is_current": version["id"] == current_version_id,
        }
        for version in versions
    ]


async def activate_dataset_version(session_id: str, version_id: int):
    session = await get_session(session_id)
    if not session or not session.get("current_dataset_id"):
        raise RuntimeError("当前会话缺少数据集")
    version = await get_dataset_version(version_id)
    if not version or version.get("session_id") != session_id or version.get("dataset_id") != session.get("current_dataset_id"):
        raise RuntimeError("数据版本不存在")

    await update_dataset(session["current_dataset_id"], current_version_id=version["id"], last_used_at=time.time())
    await update_session(
        session_id,
        current_dataset_id=session["current_dataset_id"],
        current_dataset_version_id=version["id"],
        data_summary=json.dumps(version.get("summary"), ensure_ascii=False) if version.get("summary") is not None else None,
    )

    metadata_snapshot = await load_metadata_snapshot(session_id, version["storage_key"])
    if metadata_snapshot is not None:
        await replace_variable_metadata(session_id, metadata_snapshot)
    return version


def _build_dataset_version_artifacts(df: pd.DataFrame) -> tuple[bytes, dict]:
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        temp_path = tmp.name
    try:
        df.to_parquet(temp_path, index=False)
        summary = summarize_dataframe(df)
        with open(temp_path, "rb") as handle:
            content = handle.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return content, summary
