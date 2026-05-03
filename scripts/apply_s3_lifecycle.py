from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="为 SPSSGO 对象存储桶应用生命周期规则。")
    parser.add_argument("--bucket", default=os.getenv("S3_BUCKET", ""))
    parser.add_argument("--endpoint-url", default=os.getenv("S3_ENDPOINT_URL", ""))
    parser.add_argument("--region", default=os.getenv("S3_REGION", ""))
    parser.add_argument("--access-key", default=os.getenv("S3_ACCESS_KEY", ""))
    parser.add_argument("--secret-key", default=os.getenv("S3_SECRET_KEY", ""))
    parser.add_argument("--config", default="ops/s3-lifecycle.example.json")
    parser.add_argument("--dry-run", action="store_true", help="只打印将要下发的配置，不真正提交")
    return parser


def load_config(path: str) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if "Rules" not in payload or not isinstance(payload["Rules"], list):
        raise ValueError("生命周期配置必须包含 Rules 数组")
    return payload


def build_client(args):
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=args.endpoint_url or None,
        region_name=args.region or None,
        aws_access_key_id=args.access_key or None,
        aws_secret_access_key=args.secret_key or None,
    )


def main() -> int:
    args = build_parser().parse_args()
    if not args.bucket:
        raise SystemExit("missing --bucket or S3_BUCKET")
    config = load_config(args.config)
    print(f"[lifecycle] bucket={args.bucket}")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("[lifecycle] dry-run complete")
        return 0

    client = build_client(args)
    client.put_bucket_lifecycle_configuration(
        Bucket=args.bucket,
        LifecycleConfiguration=config,
    )
    print("[lifecycle] configuration applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
