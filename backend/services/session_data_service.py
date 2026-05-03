# -*- coding: utf-8 -*-
"""Session-scoped dataset source resolution and loading helpers."""

from contextlib import contextmanager

import pandas as pd
from fastapi import HTTPException

from backend.config import IS_DEVELOPMENT
from backend.database import get_current_dataset_version_for_session
from backend.services.file_service import find_data_file_name, load_dataframe
from backend.storage import storage_service

LEGACY_UPLOAD_COMPAT_MESSAGE = "当前会话仍停留在旧上传兼容路径，请重新上传数据文件以生成标准化数据版本。"


def allow_legacy_upload_reads(user: dict | None) -> bool:
    return bool(IS_DEVELOPMENT or (user and user.get("role") == "admin"))


async def resolve_session_data_source(
    session_id: str,
    *,
    allow_legacy_fallback: bool = False,
) -> dict:
    version = await get_current_dataset_version_for_session(session_id)
    if version:
        return {
            "session_id": session_id,
            "storage_category": "datasets",
            "storage_key": version["storage_key"],
            "filename": version["storage_key"],
            "dataset_version_id": version.get("id"),
            "dataset_version_no": version.get("version_no"),
            "source": "dataset_version",
        }

    data_file_name = find_data_file_name(session_id)
    if not data_file_name:
        raise HTTPException(404, "未找到数据文件")
    if not allow_legacy_fallback:
        raise HTTPException(409, LEGACY_UPLOAD_COMPAT_MESSAGE)
    return {
        "session_id": session_id,
        "storage_category": "uploads",
        "storage_key": data_file_name,
        "filename": data_file_name,
        "dataset_version_id": None,
        "dataset_version_no": None,
        "source": "legacy_upload",
    }


@contextmanager
def materialized_session_data(data_source: dict):
    path = storage_service.materialize_file(
        data_source["storage_category"],
        data_source["session_id"],
        data_source["storage_key"],
    )
    try:
        yield path
    finally:
        storage_service.release_materialized(path)


async def load_session_dataframe(
    session_id: str,
    *,
    allow_legacy_fallback: bool = False,
    data_source: dict | None = None,
) -> pd.DataFrame:
    source = data_source or await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )
    with materialized_session_data(source) as data_file:
        return load_dataframe(data_file)
