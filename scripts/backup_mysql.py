from __future__ import annotations

import argparse
import datetime as dt
import gzip
import os
from pathlib import Path

import pymysql
from pymysql.converters import escape_item


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="为 SPSSGO 生成 MySQL 逻辑备份。")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", "3306")))
    parser.add_argument("--user", default=os.getenv("MYSQL_USER", "root"))
    parser.add_argument("--password", default=os.getenv("MYSQL_PASSWORD", ""))
    parser.add_argument("--database", default=os.getenv("MYSQL_DATABASE", "data_analysis"))
    parser.add_argument("--output-dir", default="backups/mysql")
    parser.add_argument("--filename", default="")
    parser.add_argument("--gzip", action="store_true", help="输出为 .sql.gz")
    parser.add_argument("--retention-days", type=int, default=7, help="自动清理早于该天数的备份；0 表示不清理")
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


def dump_database(conn, database: str, handle) -> None:
    write = handle.write
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    write(f"-- SPSSGO MySQL backup\n-- database: {database}\n-- generated_at: {timestamp}\n\n")
    write("SET NAMES utf8mb4;\n")
    write("SET FOREIGN_KEY_CHECKS=0;\n\n")

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            (database,),
        )
        tables = [row[0] for row in cur.fetchall()]

    for table in tables:
        dump_table_schema(conn, table, write)
        dump_table_rows(conn, table, write)

    write("SET FOREIGN_KEY_CHECKS=1;\n")


def dump_table_schema(conn, table: str, write) -> None:
    with conn.cursor() as cur:
        cur.execute(f"SHOW CREATE TABLE `{table}`")
        row = cur.fetchone()
    create_sql = row[1]
    write(f"--\n-- Table structure for `{table}`\n--\n\n")
    write(f"DROP TABLE IF EXISTS `{table}`;\n")
    write(f"{create_sql};\n\n")


def dump_table_rows(conn, table: str, write, batch_size: int = 500) -> None:
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM `{table}`")
        columns = [desc[0] for desc in cur.description]
        column_sql = ", ".join(f"`{name}`" for name in columns)
        write(f"--\n-- Dumping data for `{table}`\n--\n\n")
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            values_sql = []
            for row in rows:
                values = ", ".join(escape_item(value, "utf8mb4") for value in row)
                values_sql.append(f"({values})")
            write(f"INSERT INTO `{table}` ({column_sql}) VALUES\n")
            write(",\n".join(values_sql))
            write(";\n")
        write("\n")


def resolve_output_path(args) -> Path:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.filename:
        filename = args.filename
    else:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        suffix = ".sql.gz" if args.gzip else ".sql"
        filename = f"spssgo-{args.database}-{stamp}{suffix}"
    return output_dir / filename


def prune_old_backups(output_dir: Path, retention_days: int) -> list[Path]:
    if retention_days <= 0 or not output_dir.exists():
        return []
    cutoff = dt.datetime.now() - dt.timedelta(days=retention_days)
    removed = []
    for path in output_dir.iterdir():
        if not path.is_file():
            continue
        modified = dt.datetime.fromtimestamp(path.stat().st_mtime)
        if modified < cutoff:
            path.unlink(missing_ok=True)
            removed.append(path)
    return removed


def main() -> int:
    args = build_parser().parse_args()
    output_path = resolve_output_path(args)
    output_dir = output_path.parent
    conn = connect(args)
    try:
        if args.gzip:
            with gzip.open(output_path, "wt", encoding="utf-8", newline="\n") as handle:
                dump_database(conn, args.database, handle)
        else:
            with output_path.open("w", encoding="utf-8", newline="\n") as handle:
                dump_database(conn, args.database, handle)
    finally:
        conn.close()

    removed = prune_old_backups(output_dir, args.retention_days)
    print(f"[backup] wrote {output_path}")
    if removed:
        print(f"[backup] pruned {len(removed)} old backup(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
