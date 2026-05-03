from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass

import pymysql
from pymysql.cursors import DictCursor


@dataclass
class ReconcileDecision:
    next_status: str
    reason: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="收尾历史遗留 jobs 状态。")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", "3306")))
    parser.add_argument("--user", default=os.getenv("MYSQL_USER", "root"))
    parser.add_argument("--password", default=os.getenv("MYSQL_PASSWORD", ""))
    parser.add_argument("--database", default=os.getenv("MYSQL_DATABASE", "data_analysis"))
    parser.add_argument("--older-than-minutes", type=int, default=30, help="只处理早于该分钟数的 queued job")
    parser.add_argument("--limit", type=int, default=200, help="最多扫描多少条 queued job")
    parser.add_argument("--apply", action="store_true", help="执行写入；默认仅 dry-run")
    return parser


def connect(args: argparse.Namespace):
    return pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        charset="utf8mb4",
        autocommit=False,
        cursorclass=DictCursor,
    )


def classify_job(row: dict, now_ts: float, older_than_seconds: int) -> ReconcileDecision | None:
    if (row.get("status") or "").lower() != "queued":
        return None
    created_at = float(row.get("created_at") or 0.0)
    if now_ts - created_at < older_than_seconds:
        return None

    started_at = row.get("started_at")
    finished_at = row.get("finished_at")
    error_message = (row.get("error_message") or "").strip()

    if finished_at is not None:
        if error_message:
            return ReconcileDecision("failed", "历史收尾：任务已结束但状态未同步，按失败补齐")
        return ReconcileDecision("succeeded", "历史收尾：任务已完成但状态停留在 queued，按成功补齐")

    if started_at is not None:
        return ReconcileDecision("failed", "历史收尾：任务曾启动但未正常收尾，按失败补齐")

    return ReconcileDecision("failed", "历史收尾：任务长时间停留 queued，按失败补齐")


def merge_progress(row: dict, decision: ReconcileDecision) -> str:
    progress = row.get("progress_json")
    parsed = {}
    if progress:
        try:
            parsed = json.loads(progress)
        except json.JSONDecodeError:
            parsed = {"raw_progress": progress}
    parsed.update(
        {
            "stage": "reconciled",
            "message": decision.reason,
            "previous_status": row.get("status"),
        }
    )
    return json.dumps(parsed, ensure_ascii=False)


def list_candidates(conn, older_than_seconds: int, limit: int) -> list[dict]:
    cutoff = time.time() - older_than_seconds
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, job_type, status, queue_name, created_at, started_at, finished_at,
                   error_message, progress_json
            FROM jobs
            WHERE status = 'queued' AND created_at <= %s
            ORDER BY created_at ASC
            LIMIT %s
            """,
            (cutoff, limit),
        )
        return list(cur.fetchall())


def apply_decision(conn, row: dict, decision: ReconcileDecision, now_ts: float) -> None:
    finished_at = row.get("finished_at")
    if finished_at is None and decision.next_status in {"failed", "succeeded"}:
        finished_at = now_ts
    error_message = (row.get("error_message") or "").strip()
    if decision.next_status == "succeeded":
        error_message = ""
    elif not error_message:
        error_message = decision.reason

    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE jobs
            SET status = %s,
                error_message = %s,
                finished_at = %s,
                progress_json = %s
            WHERE id = %s
            """,
            (
                decision.next_status,
                error_message,
                finished_at,
                merge_progress(row, decision),
                row["id"],
            ),
        )


def main() -> int:
    args = build_parser().parse_args()
    older_than_seconds = max(args.older_than_minutes, 1) * 60
    now_ts = time.time()
    conn = connect(args)
    try:
        rows = list_candidates(conn, older_than_seconds, args.limit)
        decisions: list[tuple[dict, ReconcileDecision]] = []
        for row in rows:
            decision = classify_job(row, now_ts, older_than_seconds)
            if decision is not None:
                decisions.append((row, decision))

        print(f"[reconcile] queued candidates={len(rows)} actionable={len(decisions)} dry_run={not args.apply}")
        for row, decision in decisions:
            print(
                f"[reconcile] {row['id']} {row['job_type']} "
                f"created_at={row.get('created_at')} started_at={row.get('started_at')} finished_at={row.get('finished_at')} "
                f"-> {decision.next_status} | {decision.reason}"
            )

        if not args.apply:
            conn.rollback()
            return 0

        for row, decision in decisions:
            apply_decision(conn, row, decision, now_ts)
        conn.commit()
        print(f"[reconcile] applied {len(decisions)} updates")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
