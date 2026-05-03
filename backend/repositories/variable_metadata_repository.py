# -*- coding: utf-8 -*-
"""变量元数据仓储，只管变量标签和编码规则，别塞数据处理算法。"""
import json
import time

import aiomysql

import backend.database as db


async def get_variable_metadata_map(session_id: str) -> dict[str, dict]:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT variable_name, var_type, display_name, value_labels_json, code_rules_json, updated_at "
                "FROM variable_metadata WHERE session_id = %s",
                (session_id,),
            )
            rows = await cur.fetchall()
    items = {}
    for row in rows:
        item = dict(row)
        item["value_labels"] = json.loads(item["value_labels_json"]) if item.get("value_labels_json") else {}
        item["code_rules"] = json.loads(item["code_rules_json"]) if item.get("code_rules_json") else {}
        items[item["variable_name"]] = item
    return items


async def upsert_variable_metadata(
    session_id: str,
    variable_name: str,
    *,
    var_type: str | None = None,
    display_name: str | None = None,
    value_labels: dict | None = None,
    code_rules: dict | list | None = None,
):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO variable_metadata
                    (session_id, variable_name, var_type, display_name, value_labels_json, code_rules_json, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    var_type = COALESCE(VALUES(var_type), var_type),
                    display_name = COALESCE(VALUES(display_name), display_name),
                    value_labels_json = COALESCE(VALUES(value_labels_json), value_labels_json),
                    code_rules_json = COALESCE(VALUES(code_rules_json), code_rules_json),
                    updated_at = VALUES(updated_at)
                """,
                (
                    session_id,
                    variable_name,
                    var_type,
                    display_name,
                    json.dumps(value_labels, ensure_ascii=False) if value_labels is not None else None,
                    json.dumps(code_rules, ensure_ascii=False) if code_rules is not None else None,
                    time.time(),
                ),
            )


async def rename_variable_metadata(session_id: str, old_name: str, new_name: str):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE variable_metadata SET variable_name = %s, updated_at = %s WHERE session_id = %s AND variable_name = %s",
                (new_name, time.time(), session_id, old_name),
            )


async def delete_variable_metadata(session_id: str, variable_name: str):
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM variable_metadata WHERE session_id = %s AND variable_name = %s",
                (session_id, variable_name),
            )


async def replace_variable_metadata(session_id: str, metadata_map: dict[str, dict] | None):
    metadata_map = metadata_map or {}
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM variable_metadata WHERE session_id = %s", (session_id,))
            for variable_name, metadata in metadata_map.items():
                await cur.execute(
                    """
                    INSERT INTO variable_metadata
                        (session_id, variable_name, var_type, display_name, value_labels_json, code_rules_json, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session_id,
                        variable_name,
                        metadata.get("var_type"),
                        metadata.get("display_name"),
                        db._json_dumps(metadata.get("value_labels") or {}),
                        db._json_dumps(metadata.get("code_rules") or {}),
                        metadata.get("updated_at") or time.time(),
                    ),
                )
