from __future__ import annotations

import importlib
import os
import posixpath
import tempfile
import uuid

try:
    ClientError = importlib.import_module("botocore.exceptions").ClientError
except Exception:  # pragma: no cover - optional until boto3/botocore installed
    ClientError = Exception

from .base import BaseStorage


class S3Storage(BaseStorage):
    def __init__(
        self,
        bucket: str,
        endpoint_url: str | None,
        region: str | None,
        access_key: str | None,
        secret_key: str | None,
        key_prefix: str = "",
    ):
        try:
            boto3 = importlib.import_module("boto3")
        except ImportError as exc:
            raise RuntimeError("使用 S3 存储需要先安装 boto3") from exc

        self.bucket = bucket
        self.key_prefix = key_prefix.strip("/")
        self.endpoint_url = endpoint_url or None
        self.region = region or None
        self.temp_dir = os.path.join(tempfile.gettempdir(), "spssgo-storage-cache")
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            aws_access_key_id=access_key or None,
            aws_secret_access_key=secret_key or None,
        )

    def initialize(self) -> None:
        os.makedirs(self.temp_dir, exist_ok=True)
        self.client.head_bucket(Bucket=self.bucket)

    def ensure_session(self, session_id: str) -> None:
        # 对象存储无需预创建目录
        return None

    def save_bytes(self, category: str, session_id: str, relative_path: str, content: bytes) -> None:
        self.client.put_object(Bucket=self.bucket, Key=self._key(category, session_id, relative_path), Body=content)

    def save_text(
        self,
        category: str,
        session_id: str,
        relative_path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        self.save_bytes(category, session_id, relative_path, content.encode(encoding))

    def read_bytes(self, category: str, session_id: str, relative_path: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=self._key(category, session_id, relative_path))
        return obj["Body"].read()

    def read_text(
        self,
        category: str,
        session_id: str,
        relative_path: str,
        encoding: str = "utf-8",
    ) -> str:
        return self.read_bytes(category, session_id, relative_path).decode(encoding)

    def exists(self, category: str, session_id: str, relative_path: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=self._key(category, session_id, relative_path))
            return True
        except ClientError:
            return False

    def list_files(self, category: str, session_id: str) -> list[str]:
        prefix = self._prefix(category, session_id)
        paginator = self.client.get_paginator("list_objects_v2")
        names = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                rel = item["Key"][len(prefix):]
                if rel and "/" not in rel:
                    names.append(rel)
        names.sort()
        return names

    def delete_session(self, session_id: str) -> None:
        for category in ("uploads", "outputs", "datasets"):
            keys = self._list_keys(category, session_id)
            if not keys:
                continue
            for start in range(0, len(keys), 1000):
                chunk = keys[start:start + 1000]
                self.client.delete_objects(
                    Bucket=self.bucket,
                    Delete={"Objects": [{"Key": key} for key in chunk]},
                )

    def materialize_file(self, category: str, session_id: str, relative_path: str) -> str:
        suffix = os.path.splitext(relative_path)[1]
        fd, temp_path = tempfile.mkstemp(prefix=f"spssgo-{session_id}-", suffix=suffix, dir=self.temp_dir)
        os.close(fd)
        with open(temp_path, "wb") as f:
            f.write(self.read_bytes(category, session_id, relative_path))
        return temp_path

    def release_materialized(self, path: str) -> None:
        if path.startswith(self.temp_dir) and os.path.exists(path):
            os.remove(path)

    def category_size(self, category: str) -> int:
        prefix = self._category_prefix(category)
        paginator = self.client.get_paginator("list_objects_v2")
        total = 0
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                total += int(item.get("Size", 0))
        return total

    def healthcheck(self) -> dict:
        marker_key = self._healthcheck_key()
        try:
            self.initialize()
            self.client.put_object(Bucket=self.bucket, Key=marker_key, Body=b"ok")
            self.client.delete_object(Bucket=self.bucket, Key=marker_key)
            return {
                "ok": True,
                "backend": "s3",
                "bucket": self.bucket,
                "endpoint_url": self.endpoint_url or "",
                "region": self.region or "",
                "write_probe": True,
            }
        except Exception as exc:
            return {
                "ok": False,
                "backend": "s3",
                "bucket": self.bucket,
                "endpoint_url": self.endpoint_url or "",
                "region": self.region or "",
                "detail": str(exc),
            }

    def _category_prefix(self, category: str) -> str:
        parts = [p for p in (self.key_prefix, category) if p]
        return "/".join(parts) + "/"

    def _prefix(self, category: str, session_id: str) -> str:
        return self._category_prefix(category) + session_id + "/"

    def _key(self, category: str, session_id: str, relative_path: str) -> str:
        normalized = relative_path.replace("\\", "/").strip("/")
        return posixpath.join(self._prefix(category, session_id), normalized)

    def _list_keys(self, category: str, session_id: str) -> list[str]:
        prefix = self._prefix(category, session_id)
        paginator = self.client.get_paginator("list_objects_v2")
        keys = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                keys.append(item["Key"])
        return keys

    def _healthcheck_key(self) -> str:
        parts = [p for p in (self.key_prefix, "healthchecks", f"ready-{uuid.uuid4().hex}.txt") if p]
        return "/".join(parts)

