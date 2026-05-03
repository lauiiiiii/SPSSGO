# -*- coding: utf-8 -*-
"""上传摄入服务，只管文件保存、解析和问卷文本落库，别把浏览导出塞进来。"""
import json
import os

from fastapi import HTTPException

from backend.config import ALLOWED_EXTENSIONS, DATA_EXTENSIONS, MAX_UPLOAD_SIZE_MB
from backend.database import update_session
from backend.file_parser import parse_data_file, parse_questionnaire
from backend.storage import storage_service


def validate_upload_file(filename: str, size_bytes: int):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件格式: {ext}")
    if size_bytes > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"文件超过 {MAX_UPLOAD_SIZE_MB}MB 限制")
    return ext


async def ingest_uploaded_file(session_id: str, session: dict, file) -> dict:
    content = await file.read()
    ext = validate_upload_file(file.filename, len(content))
    storage_service.save_bytes("uploads", session_id, file.filename, content)
    filepath = storage_service.materialize_file("uploads", session_id, file.filename)

    result = {"filename": file.filename, "type": ext}
    try:
        if ext in DATA_EXTENSIONS:
            try:
                _, summary = parse_data_file(filepath)
                await update_session(session_id, data_summary=json.dumps(summary, ensure_ascii=False))
                result["data_summary"] = summary
            except Exception as exc:
                raise HTTPException(400, f"文件解析失败: {str(exc)}")
        elif ext in (".docx", ".doc"):
            try:
                text = parse_questionnaire(filepath)
                storage_service.save_text(
                    "uploads",
                    session_id,
                    f"meta/{file.filename}.json",
                    json.dumps({"filename": file.filename, "content": text}, ensure_ascii=False),
                )
                prev = session.get("questionnaire_text", "") or ""
                combined = (prev + "\n\n--- " + file.filename + " ---\n" + text).strip()
                await update_session(session_id, questionnaire_text=combined)
                result["questionnaire_preview"] = text[:500]
            except Exception as exc:
                raise HTTPException(400, f"问卷解析失败: {str(exc)}")
    finally:
        storage_service.release_materialized(filepath)

    return result


def load_questionnaire_content(session_id: str, filename: str) -> dict:
    meta_path = f"meta/{filename}.json"
    if storage_service.exists("uploads", session_id, meta_path):
        data = json.loads(storage_service.read_text("uploads", session_id, meta_path))
        return {"filename": filename, "content": data.get("content", "")}
    if not storage_service.exists("uploads", session_id, filename):
        raise HTTPException(404, "文件不存在")

    path = storage_service.materialize_file("uploads", session_id, filename)
    try:
        return {"filename": filename, "content": parse_questionnaire(path)}
    except Exception as exc:
        raise HTTPException(500, f"解析失败: {str(exc)}")
    finally:
        storage_service.release_materialized(path)
