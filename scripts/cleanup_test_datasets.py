#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理压测产生的测试数据集
用法:
  python scripts/cleanup_test_datasets.py          # 预览模式（不删除）
  python scripts/cleanup_test_datasets.py --delete # 正式删除
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from dotenv import load_dotenv

load_dotenv()

# 本地直连配置（与 start-backend.bat 一致）
DB_CONFIG = dict(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="facai888",
    database="data_analysis",
    charset="utf8mb4",
)

# 需要清理的测试文件名（压测使用的示例文件）
TEST_FILENAMES = [
    "category_summary_sample.csv",
]

DELETE_MODE = "--delete" in sys.argv
AUTO_YES = "--yes" in sys.argv


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("=" * 60)
    print(f"模式: {'【正式删除】' if DELETE_MODE else '【预览，不删除】'}")
    print("=" * 60)

    # 总量统计
    cur.execute("SELECT COUNT(*) FROM datasets")
    total = cur.fetchone()[0]
    print(f"\ndatasets 表总条数: {total}")

    cur.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cur.fetchone()[0]
    print(f"sessions 表总条数: {total_sessions}")

    # 各测试文件名统计
    to_delete_session_ids = []
    for filename in TEST_FILENAMES:
        cur.execute(
            "SELECT session_id FROM datasets WHERE original_filename = %s",
            (filename,)
        )
        rows = cur.fetchall()
        session_ids = [r[0] for r in rows]
        print(f"\n文件名 '{filename}': {len(session_ids)} 条")
        to_delete_session_ids.extend(session_ids)

    print(f"\n合计待清理数据集: {len(to_delete_session_ids)} 条")

    if not to_delete_session_ids:
        print("无需清理。")
        conn.close()
        return

    if not DELETE_MODE:
        print("\n（预览模式，实际未删除。加 --delete 参数执行真正删除）")
        conn.close()
        return

    # 正式删除：逐批删除 sessions（级联删除 datasets / dataset_versions / results）
    BATCH = 200
    deleted = 0
    failed = 0

    # 检查外键关联表
    for table in ["datasets", "dataset_versions", "results"]:
        try:
            placeholders = ",".join(["%s"] * len(to_delete_session_ids))
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE session_id IN ({placeholders})", to_delete_session_ids)
            cnt = cur.fetchone()[0]
            print(f"  关联 {table}: {cnt} 条将被删除")
        except Exception as e:
            print(f"  关联 {table}: 查询失败({e})")

    if not AUTO_YES:
        confirm = input("\n确认删除以上数据？输入 YES 继续: ")
        if confirm.strip() != "YES":
            print("已取消。")
            conn.close()
            return
    else:
        print("\n（--yes 自动确认，开始删除...）")

    for i in range(0, len(to_delete_session_ids), BATCH):
        batch = to_delete_session_ids[i:i+BATCH]
        placeholders = ",".join(["%s"] * len(batch))
        try:
            cur.execute(f"DELETE FROM sessions WHERE id IN ({placeholders})", batch)
            conn.commit()
            deleted += len(batch)
            print(f"  已删除 {deleted}/{len(to_delete_session_ids)}...")
        except Exception as e:
            conn.rollback()
            failed += len(batch)
            print(f"  批次 {i}-{i+BATCH} 删除失败: {e}")

    print(f"\n完成：删除 {deleted} 条，失败 {failed} 条")

    cur.execute("SELECT COUNT(*) FROM datasets")
    remaining = cur.fetchone()[0]
    print(f"datasets 表剩余: {remaining} 条")

    conn.close()


if __name__ == "__main__":
    main()
