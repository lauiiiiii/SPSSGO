# -*- coding: utf-8 -*-
"""公开分享报告服务，只处理快照校验和分享链接生成，别把工作台状态塞进来。"""
import json
import time

from fastapi import HTTPException

from backend.repositories.shared_report_repository import (
    create_shared_report,
    delete_shared_reports_for_exact_result_ids,
    get_shared_report_by_token,
)
from backend.security_utils import hash_password, verify_password
from backend.services.session_access import get_session_or_404

VALID_SHARE_EXPIRY_DAYS = {1, 3, 7, 30}


def _normalize_tag_list(values) -> list[str]:
    if not isinstance(values, list):
        return []
    tags = []
    for value in values:
        text = str(value or "").strip()
        if text:
            tags.append(text[:120])
    return tags[:20]


def _normalize_display_results(values) -> list[dict]:
    if not isinstance(values, list) or not values:
        raise HTTPException(400, "缺少可分享的分析报告内容")
    try:
        normalized = json.loads(json.dumps(values, ensure_ascii=False))
    except Exception as exc:
        raise HTTPException(400, "分析报告内容格式不合法") from exc
    if not isinstance(normalized, list) or not normalized:
        raise HTTPException(400, "缺少可分享的分析报告内容")
    return normalized


def _normalize_ai_result(value) -> str:
    text = str(value or "").strip()
    return text[:20000]


def _normalize_expiry_days(value) -> int:
    try:
        days = int(value)
    except Exception as exc:
        raise HTTPException(400, "分享有效期不合法") from exc
    if days not in VALID_SHARE_EXPIRY_DAYS:
        raise HTTPException(400, "分享有效期只支持 1 天、3 天、7 天、30 天")
    return days


def _normalize_password(value) -> str:
    password = str(value or "").strip()
    if not password:
        return ""
    if len(password) < 4:
        raise HTTPException(400, "访问密码至少 4 位")
    if len(password) > 64:
        raise HTTPException(400, "访问密码不能超过 64 位")
    return password


def _normalize_result_ids(values) -> list[int]:
    if not isinstance(values, list):
        return []
    result_ids: list[int] = []
    seen: set[int] = set()
    for value in values:
        try:
            result_id = int(value)
        except Exception:
            continue
        if result_id <= 0 or result_id in seen:
            continue
        seen.add(result_id)
        result_ids.append(result_id)
    return result_ids[:100]


def _raise_share_error(status_code: int, message: str, code: str) -> None:
    raise HTTPException(status_code, {"message": message, "code": code})


def _normalize_public_payload(record: dict) -> dict:
    payload = record.get("payload") or {}
    return {
        "share_token": record["share_token"],
        "created_at": record["created_at"],
        "expires_at": record.get("expires_at"),
        "requires_password": bool(record.get("password_hash")),
        "report_title": str(payload.get("report_title") or "分析报告"),
        "report_meta_tags": _normalize_tag_list(payload.get("report_meta_tags")),
        "display_results": _normalize_display_results(payload.get("display_results")),
        "ai_result": _normalize_ai_result(payload.get("ai_result")),
    }


def _ensure_share_available(record: dict | None) -> dict:
    if not record:
        _raise_share_error(404, "分享报告不存在或已失效", "share_not_found")
    expires_at = float(record.get("expires_at") or 0)
    if expires_at and time.time() > expires_at:
        _raise_share_error(410, "分享链接已过期", "share_expired")
    return record


async def create_shared_report_snapshot(body: dict | None, user: dict) -> dict:
    """把当前报告页快照固化成公开链接。"""
    if body is None:
        raise HTTPException(400, "请求体为空")

    session_id = str(body.get("session_id") or "").strip()
    if not session_id:
        raise HTTPException(400, "缺少会话标识")
    await get_session_or_404(session_id, user)

    report_title = str(body.get("report_title") or "").strip() or "分析报告"
    expiry_days = _normalize_expiry_days(body.get("expiry_days", 7))
    password = _normalize_password(body.get("password"))
    result_ids = _normalize_result_ids(body.get("result_ids"))
    expires_at = time.time() + expiry_days * 86400
    payload = {
        "report_title": report_title[:500],
        "report_meta_tags": _normalize_tag_list(body.get("report_meta_tags")),
        "result_ids": result_ids,
        "display_results": _normalize_display_results(body.get("display_results")),
        "ai_result": _normalize_ai_result(body.get("ai_result")),
    }
    try:
        record = await create_shared_report(
            session_id,
            int(user["id"]),
            payload,
            expires_at=expires_at,
            password_hash=hash_password(password) if password else None,
        )
    except RuntimeError as exc:
        raise HTTPException(500, str(exc)) from exc
    if result_ids:
        await delete_shared_reports_for_exact_result_ids(
            session_id,
            result_ids,
            report_title=payload["report_title"],
            exclude_share_token=record["share_token"],
        )
    return {
        "success": True,
        "share_token": record["share_token"],
        "share_path": f"/share/report/{record['share_token']}",
        "created_at": record["created_at"],
        "expires_at": record["expires_at"],
        "requires_password": bool(password),
    }


async def get_public_shared_report(share_token: str) -> dict:
    """公开读取分享状态；加密链接只返回状态，不直接给内容。"""
    token = str(share_token or "").strip()
    if not token:
        raise HTTPException(400, "缺少分享标识")

    record = _ensure_share_available(await get_shared_report_by_token(token))
    payload = _normalize_public_payload(record)
    if payload["requires_password"]:
        return {
            "share_token": payload["share_token"],
            "created_at": payload["created_at"],
            "expires_at": payload["expires_at"],
            "requires_password": True,
            "report_title": payload["report_title"],
        }
    return payload


async def access_public_shared_report(share_token: str, body: dict | None) -> dict:
    """校验分享密码后返回完整报告。"""
    token = str(share_token or "").strip()
    if not token:
        raise HTTPException(400, "缺少分享标识")

    record = _ensure_share_available(await get_shared_report_by_token(token))
    password_hash = record.get("password_hash")
    if password_hash:
        password = _normalize_password((body or {}).get("password"))
        if not password:
            _raise_share_error(401, "分享报告已加密，请输入访问密码", "share_password_required")
        if not verify_password(password, password_hash):
            _raise_share_error(403, "访问密码错误", "share_password_invalid")
    return _normalize_public_payload(record)
