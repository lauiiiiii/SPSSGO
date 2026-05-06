# -*- coding: utf-8 -*-
import json
import os

import pandas as pd
from fastapi import HTTPException

from backend.app_runtime import download_response
from backend.config import DATA_EXTENSIONS
from backend.database import get_session, get_variable_metadata_map, update_session
from backend.file_parser import parse_data_file
from backend.services.data_view_service import build_data_preview, export_data_file, get_variable_values, get_variables
from backend.services.file_service import upload_files
from backend.services.session_data_service import resolve_session_data_source
from backend.services.upload_ingest_service import ingest_uploaded_file, load_questionnaire_content
from backend.storage import storage_service

async def upload_file_for_session(session_id: str, file):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    return await ingest_uploaded_file(session_id, session, file)


async def list_files_for_session(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    data_files, quest_files = [], []
    for fname in upload_files(session_id):
        ext = os.path.splitext(fname)[1].lower()
        if ext in DATA_EXTENSIONS:
            data_files.append({"name": fname, "type": ext})
        elif ext in (".docx", ".doc"):
            quest_files.append({"name": fname, "type": ext})
    return {"data_files": data_files, "quest_files": quest_files}


async def get_questionnaire_content_for_session(session_id: str, filename: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    return load_questionnaire_content(session_id, filename)


async def build_data_preview_for_session(session_id: str, limit: int = 100, *, allow_legacy_fallback: bool = False):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    # 这里保留旧 patch 点，测试和兼容调用还在拦这个入口。
    data_source = await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )

    path = None
    try:
        path = storage_service.materialize_file(
            data_source["storage_category"],
            session_id,
            data_source["storage_key"],
        )
    except FileNotFoundError:
        raise HTTPException(404, "数据文件不存在，可能已被清理，请尝试重新上传")
    except Exception as exc:
        raise HTTPException(422, f"数据文件读取失败: {str(exc)}")

    try:
        try:
            df, _ = parse_data_file(path)
        except ValueError as exc:
            raise HTTPException(422, f"数据格式解析失败: {str(exc)}")
        except Exception as exc:
            raise HTTPException(422, f"数据解析失败: {str(exc)}")

        # 空数据兜底：返回空 rows 但不抛异常
        if len(df) == 0 or len(df.columns) == 0:
            return {
                "filename": data_source["filename"],
                "total_rows": len(df),
                "total_cols": len(df.columns),
                "headers": [str(c) for c in df.columns],
                "rows": [],
                "source": data_source["source"],
                "dataset_version_id": data_source["dataset_version_id"],
                "dataset_version_no": data_source["dataset_version_no"],
            }

        sample = df.head(min(limit, 200))
        headers = [str(c) for c in sample.columns]
        rows = []
        for _, row in sample.iterrows():
            rows.append([
                "" if pd.isna(v) else (str(int(v)) if isinstance(v, float) and v == int(v) else str(v))
                for v in row
            ])
        return {
            "filename": data_source["filename"],
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "headers": headers,
            "rows": rows,
            "source": data_source["source"],
            "dataset_version_id": data_source["dataset_version_id"],
            "dataset_version_no": data_source["dataset_version_no"],
        }
    finally:
        if path:
            storage_service.release_materialized(path)


async def get_variable_values_for_session(session_id: str, column_name: str, limit: int = 200, *, allow_legacy_fallback: bool = False):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    try:
        return await get_variable_values(
            session_id,
            column_name,
            await get_variable_metadata_map(session_id),
            limit,
            allow_legacy_fallback=allow_legacy_fallback,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"变量取值读取失败: {str(exc)}")


async def download_data_file_for_session(session_id: str, *, allow_legacy_fallback: bool = False):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    # 这里保留旧导入名，测试和兼容调用还在 patch 它。
    data_source = await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )
    content = storage_service.read_bytes(data_source["storage_category"], session_id, data_source["storage_key"])
    return download_response(content, data_source["filename"], "application/octet-stream")

async def export_data_file_for_session(session_id: str, export_format: str, *, allow_legacy_fallback: bool = False):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    try:
        return await export_data_file(
            session_id,
            export_format,
            allow_legacy_fallback=allow_legacy_fallback,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"导出失败: {str(exc)}")


async def get_variables_for_session(session_id: str, *, allow_legacy_fallback: bool = False):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    try:
        return await get_variables(
            session_id,
            await get_variable_metadata_map(session_id),
            allow_legacy_fallback=allow_legacy_fallback,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"变量读取失败: {str(exc)}")

