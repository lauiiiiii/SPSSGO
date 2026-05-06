# -*- coding: utf-8 -*-
"""数据集文件夹仓储，只管文件夹和数据集归属，别塞页面展示逻辑。"""
import time

import aiomysql

import backend.database as db


async def list_folders_for_owner(owner_id: int) -> list[dict]:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT
                    f.id,
                    f.name,
                    f.created_at,
                    d.session_id
                FROM dataset_folders f
                LEFT JOIN dataset_folder_items fi ON fi.folder_id = f.id
                LEFT JOIN datasets d ON d.id = fi.dataset_id
                WHERE f.owner_id = %s
                ORDER BY f.created_at ASC, f.id ASC
                """,
                (owner_id,),
            )
            rows = await cur.fetchall()

    folders: dict[int, dict] = {}
    for row in rows:
        folder_id = row["id"]
        if folder_id not in folders:
            folders[folder_id] = {
                "id": folder_id,
                "name": row["name"] or "",
                "created_at": row["created_at"],
                "sessionIds": [],
            }
        if row.get("session_id"):
            folders[folder_id]["sessionIds"].append(row["session_id"])
    return list(folders.values())


async def get_folder(folder_id: int) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM dataset_folders WHERE id = %s", (folder_id,))
            row = await cur.fetchone()
    return dict(row) if row else None


async def get_folder_by_owner_name(owner_id: int, name: str) -> dict | None:
    async with db._pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM dataset_folders WHERE owner_id = %s AND name = %s LIMIT 1",
                (owner_id, name),
            )
            row = await cur.fetchone()
    return dict(row) if row else None


async def create_folder(owner_id: int, name: str) -> dict:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO dataset_folders (owner_id, name, created_at) VALUES (%s, %s, %s)",
                (owner_id, name, time.time()),
            )
            folder_id = cur.lastrowid
    folder = await get_folder(folder_id)
    return {
        "id": folder_id,
        "name": folder["name"] if folder else name,
        "created_at": folder["created_at"] if folder else None,
        "sessionIds": [],
    }


async def rename_folder(folder_id: int, name: str) -> None:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE dataset_folders SET name = %s WHERE id = %s", (name, folder_id))


async def delete_folder(folder_id: int) -> None:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM dataset_folders WHERE id = %s", (folder_id,))


async def set_dataset_folder(dataset_id: int, folder_id: int | None) -> None:
    async with db._pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM dataset_folder_items WHERE dataset_id = %s", (dataset_id,))
            if folder_id:
                await cur.execute(
                    """
                    INSERT INTO dataset_folder_items (folder_id, dataset_id, created_at)
                    VALUES (%s, %s, %s)
                    """,
                    (folder_id, dataset_id, time.time()),
                )
