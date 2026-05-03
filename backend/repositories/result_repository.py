# -*- coding: utf-8 -*-
"""分析结果仓储，只管 results 表，别塞报告生成和分析执行。"""
import json
import time

import aiomysql

import backend.database as db
from backend.domain import normalize_analysis_sections


async def save_result(
    session_id,
    analysis_name,
    table_headers,
    table_rows,
    description,
    code="",
    sections=None,
    *,
    owner_id: int | None = None,
    job_id: str | None = None,
    dataset_version_id: int | None = None,
):
    sections_str = json.dumps(sections, ensure_ascii=False) if sections else None
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO results (session_id, owner_id, job_id, dataset_version_id, analysis_name, table_headers, table_rows, description, sections_json, code, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    session_id, owner_id, job_id, dataset_version_id, analysis_name,
                    json.dumps(table_headers, ensure_ascii=False),
                    json.dumps(table_rows, ensure_ascii=False),
                    description, sections_str, code, time.time(),
                ),
            )


async def get_results(session_id: str) -> list[dict]:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT
                    r.*,
                    dv.version_no AS dataset_version_no
                FROM results r
                LEFT JOIN dataset_versions dv ON dv.id = r.dataset_version_id
                WHERE r.session_id = %s
                ORDER BY r.id
                """,
                (session_id,),
            )
            rows = await cur.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["table_headers"] = db._parse_json(d.get("table_headers"), [])
        d["table_rows"] = db._parse_json(d.get("table_rows"), [])
        d["sections"] = normalize_analysis_sections(db._parse_json(d.get("sections_json"), None))
        results.append(d)
    return results


async def rename_result(session_id: str, result_id: int, analysis_name: str) -> bool:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE results SET analysis_name = %s WHERE id = %s AND session_id = %s",
                (analysis_name, result_id, session_id),
            )
            return cur.rowcount > 0


async def delete_result(session_id: str, result_id: int) -> bool:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM results WHERE id = %s AND session_id = %s",
                (result_id, session_id),
            )
            return cur.rowcount > 0


async def delete_results_for_job(job_id: str):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM results WHERE job_id = %s", (job_id,))
