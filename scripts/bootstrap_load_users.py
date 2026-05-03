from __future__ import annotations

import argparse
import asyncio
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import close_db, create_user, get_user_by_username, init_db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap load-test users directly in the database.")
    parser.add_argument("--prefix", default="loaduser")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--password", required=True)
    parser.add_argument("--role", default="user")
    parser.add_argument("--stop-on-existing", action="store_true")
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    await init_db()
    created = 0
    skipped = 0

    try:
        for index in range(args.start, args.start + args.count):
            username = f"{args.prefix}{index}"
            existing = await get_user_by_username(username)
            if existing:
                skipped += 1
                print(f"[bootstrap-users] skip existing: {username}")
                if args.stop_on_existing:
                    break
                continue
            await create_user(username, args.password, role=args.role)
            created += 1
            print(f"[bootstrap-users] created: {username}")
    finally:
        await close_db()

    print(f"[bootstrap-users] done: created={created}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
