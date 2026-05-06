# -*- coding: utf-8 -*-
"""清理 datasets / dataset_versions 表中 storage_key 的 Windows 反斜杠和冗余路径前缀。

部分老数据的 storage_key 存成了完整路径（如 datasets\\session\\file.parquet），
正常应该是纯文件名（file.parquet）。这个脚本扫描并修复这类脏数据。
"""

import asyncio
import os
import sys

# 把项目根目录加入路径，才能 import backend
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import backend.database as db


async def _fetch_rows(conn, table: str):
    async with conn.cursor() as cur:
        await cur.execute(
            f"SELECT id, session_id, storage_key FROM {table} WHERE storage_key LIKE %s",
            ("%\\%",),
        )
        return await cur.fetchall()


def _clean_storage_key(session_id: str, raw: str) -> str:
    """把 storage_key 还原为纯文件名。

    常见脏数据模式：
    - datasets\\session_id\\filename.parquet
    - uploads\\session_id\\filename.xlsx
    - datasets/session_id/filename.parquet
    - session_id\\filename.parquet
    - filename.parquet   (已经是正常的)
    """
    cleaned = raw.replace("\\", "/")

    # 去掉已知的冗余前缀：datasets/<session_id>/ 或 uploads/<session_id>/
    for prefix in (f"datasets/{session_id}/", f"uploads/{session_id}/"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break

    # 如果还有 session_id/ 前缀，也去掉（某些旧数据可能只有这层）
    if cleaned.startswith(f"{session_id}/"):
        cleaned = cleaned[len(session_id) + 1 :]

    return cleaned


async def main():
    await db.init_db()
    if not db._pool:
        print("数据库连接失败")
        return 1

    total_fixed = 0

    async with db._pool.acquire() as conn:
        # 1. 修复 datasets 表
        rows = await _fetch_rows(conn, "datasets")
        if rows:
            print(f"发现 {len(rows)} 条 datasets 脏数据")
            for row_id, session_id, old_key in rows:
                new_key = _clean_storage_key(session_id, old_key)
                if new_key != old_key:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "UPDATE datasets SET storage_key = %s WHERE id = %s",
                            (new_key, row_id),
                        )
                    print(f"  datasets id={row_id}: {old_key!r} -> {new_key!r}")
                    total_fixed += 1
                else:
                    print(f"  datasets id={row_id}: 无需修改 {old_key!r}")
        else:
            print("datasets 表没有发现脏数据")

        # 2. 修复 dataset_versions 表
        rows = await _fetch_rows(conn, "dataset_versions")
        if rows:
            print(f"发现 {len(rows)} 条 dataset_versions 脏数据")
            for row_id, session_id, old_key in rows:
                new_key = _clean_storage_key(session_id, old_key)
                if new_key != old_key:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "UPDATE dataset_versions SET storage_key = %s WHERE id = %s",
                            (new_key, row_id),
                        )
                    print(f"  dataset_versions id={row_id}: {old_key!r} -> {new_key!r}")
                    total_fixed += 1
                else:
                    print(f"  dataset_versions id={row_id}: 无需修改 {old_key!r}")
        else:
            print("dataset_versions 表没有发现脏数据")

    print(f"\n共修复 {total_fixed} 条记录")
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
