from __future__ import annotations

import argparse
import gzip
import os
from pathlib import Path

import pymysql


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从 SPSSGO 逻辑备份恢复 MySQL 数据。")
    parser.add_argument("input", help="输入 .sql 或 .sql.gz 备份文件路径")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", "3306")))
    parser.add_argument("--user", default=os.getenv("MYSQL_USER", "root"))
    parser.add_argument("--password", default=os.getenv("MYSQL_PASSWORD", ""))
    parser.add_argument("--database", default=os.getenv("MYSQL_DATABASE", "data_analysis"))
    parser.add_argument("--stop-on-error", action="store_true", help="遇到 SQL 错误立即终止")
    parser.add_argument("--dry-run", action="store_true", help="只解析 SQL，不执行恢复")
    return parser


def connect(args):
    return pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.Cursor,
    )


def open_sql_input(path: str):
    target = Path(path)
    if target.suffix.lower() == ".gz":
        return gzip.open(target, "rt", encoding="utf-8", newline="")
    return target.open("r", encoding="utf-8", newline="")


def iter_sql_statements(text: str):
    buffer: list[str] = []
    in_single = False
    in_double = False
    escape = False

    for raw_line in text.splitlines(keepends=True):
        line = raw_line.lstrip()
        if not in_single and not in_double and (line.startswith("--") or line.startswith("#")):
            continue

        index = 0
        while index < len(raw_line):
            char = raw_line[index]
            if escape:
                buffer.append(char)
                escape = False
                index += 1
                continue

            if char == "\\" and (in_single or in_double):
                buffer.append(char)
                escape = True
                index += 1
                continue

            if char == "'" and not in_double:
                in_single = not in_single
                buffer.append(char)
                index += 1
                continue

            if char == '"' and not in_single:
                in_double = not in_double
                buffer.append(char)
                index += 1
                continue

            if char == ";" and not in_single and not in_double:
                statement = "".join(buffer).strip()
                if statement:
                    yield statement
                buffer = []
                index += 1
                continue

            buffer.append(char)
            index += 1

    tail = "".join(buffer).strip()
    if tail:
        yield tail


def execute_restore(conn, sql_text: str, *, stop_on_error: bool = False) -> tuple[int, list[str]]:
    executed = 0
    errors: list[str] = []
    with conn.cursor() as cur:
        for statement in iter_sql_statements(sql_text):
            try:
                cur.execute(statement)
                executed += 1
            except Exception as exc:
                message = f"{type(exc).__name__}: {exc}"
                errors.append(message)
                if stop_on_error:
                    raise RuntimeError(message) from exc
    return executed, errors


def main() -> int:
    args = build_parser().parse_args()
    with open_sql_input(args.input) as handle:
        sql_text = handle.read()

    statement_count = sum(1 for _ in iter_sql_statements(sql_text))
    print(f"[restore] parsed {statement_count} statements from {args.input}")
    if args.dry_run:
        print("[restore] dry-run complete")
        return 0

    conn = connect(args)
    try:
        executed, errors = execute_restore(conn, sql_text, stop_on_error=args.stop_on_error)
    finally:
        conn.close()

    print(f"[restore] executed {executed} statements")
    if errors:
        print(f"[restore] encountered {len(errors)} error(s)")
        for error in errors[:10]:
            print(f"  - {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
