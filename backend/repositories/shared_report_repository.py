# -*- coding: utf-8 -*-
"""分享报告仓储，只管 shared_reports 表，别把路由参数和页面拼装塞进来。"""
import json
import secrets
import time

import aiomysql

import backend.database as db


def _make_share_token() -> str:
    return secrets.token_urlsafe(18).replace("-", "").replace("_", "")


def _normalize_result_ids(values) -> list[int]:
    result_ids: list[int] = []
    seen: set[int] = set()
    for value in values or []:
        try:
            result_id = int(value)
        except Exception:
            continue
        if result_id <= 0 or result_id in seen:
            continue
        seen.add(result_id)
        result_ids.append(result_id)
    return result_ids


def _payload_result_id_set(record: dict) -> set[int]:
    payload = record.get("payload") or {}
    return set(_normalize_result_ids(payload.get("result_ids")))


def _payload_report_title(record: dict) -> str:
    payload = record.get("payload") or {}
    return str(payload.get("report_title") or "").strip()


async def _list_shared_reports_for_session(session_id: str) -> list[dict]:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT id, share_token, session_id, owner_id, payload_json, expires_at, password_hash, created_at
                FROM shared_reports
                WHERE session_id = %s
                """,
                (session_id,),
            )
            rows = await cur.fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["payload"] = db._parse_json(item.pop("payload_json", None), {})
        items.append(item)
    return items


async def _delete_shared_reports_by_ids(ids: list[int]) -> int:
    if not ids:
        return 0
    placeholders = ", ".join(["%s"] * len(ids))
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"DELETE FROM shared_reports WHERE id IN ({placeholders})",
                tuple(ids),
            )
            return cur.rowcount


async def create_shared_report(
    session_id: str,
    owner_id: int,
    payload: dict,
    *,
    expires_at: float,
    password_hash: str | None = None,
) -> dict:
    payload_json = json.dumps(payload, ensure_ascii=False)
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            for _ in range(5):
                share_token = _make_share_token()
                created_at = time.time()
                try:
                    await cur.execute(
                        """
                        INSERT INTO shared_reports (share_token, session_id, owner_id, payload_json, expires_at, password_hash, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (share_token, session_id, owner_id, payload_json, expires_at, password_hash, created_at),
                    )
                    return {
                        "share_token": share_token,
                        "created_at": created_at,
                        "expires_at": expires_at,
                    }
                except aiomysql.IntegrityError:
                    continue
    raise RuntimeError("分享链接生成失败，请稍后重试")


async def delete_shared_reports_for_exact_result_ids(
    session_id: str,
    result_ids: list[int],
    *,
    report_title: str = "",
    exclude_share_token: str | None = None,
) -> int:
    target_ids = set(_normalize_result_ids(result_ids))
    normalized_title = str(report_title or "").strip()
    if not session_id or (not target_ids and not normalized_title):
        return 0
    matched_ids = []
    for record in await _list_shared_reports_for_session(session_id):
        if exclude_share_token and record.get("share_token") == exclude_share_token:
            continue
        payload_ids = _payload_result_id_set(record)
        if payload_ids == target_ids:
            matched_ids.append(int(record["id"]))
            continue
        if not payload_ids and normalized_title and _payload_report_title(record) == normalized_title:
            matched_ids.append(int(record["id"]))
    return await _delete_shared_reports_by_ids(matched_ids)


async def delete_shared_reports_for_overlapping_result_ids(
    session_id: str,
    result_ids: list[int],
    *,
    report_title: str = "",
) -> int:
    target_ids = set(_normalize_result_ids(result_ids))
    normalized_title = str(report_title or "").strip()
    if not session_id or (not target_ids and not normalized_title):
        return 0
    matched_ids = []
    for record in await _list_shared_reports_for_session(session_id):
        payload_ids = _payload_result_id_set(record)
        if payload_ids & target_ids:
            matched_ids.append(int(record["id"]))
            continue
        if not payload_ids and normalized_title and _payload_report_title(record) == normalized_title:
            matched_ids.append(int(record["id"]))
    return await _delete_shared_reports_by_ids(matched_ids)


async def get_shared_report_by_token(share_token: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT id, share_token, session_id, owner_id, payload_json, expires_at, password_hash, created_at
                FROM shared_reports
                WHERE share_token = %s
                LIMIT 1
                """,
                (share_token,),
            )
            row = await cur.fetchone()
    if not row:
        return None

    item = dict(row)
    item["payload"] = db._parse_json(item.pop("payload_json", None), {})
    return item
