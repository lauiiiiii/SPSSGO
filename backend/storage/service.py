from __future__ import annotations

from backend.config import (
    STORAGE_BACKEND,
    LOCAL_STORAGE_ROOT,
    S3_BUCKET,
    S3_ENDPOINT_URL,
    S3_REGION,
    S3_ACCESS_KEY,
    S3_SECRET_KEY,
    S3_KEY_PREFIX,
)
from .local import LocalStorage


def _build_storage():
    backend = (STORAGE_BACKEND or "local").lower()
    if backend == "s3":
        from .s3 import S3Storage

        return S3Storage(
            bucket=S3_BUCKET,
            endpoint_url=S3_ENDPOINT_URL,
            region=S3_REGION,
            access_key=S3_ACCESS_KEY,
            secret_key=S3_SECRET_KEY,
            key_prefix=S3_KEY_PREFIX,
        )
    return LocalStorage(root_dir=LOCAL_STORAGE_ROOT)


storage_service = _build_storage()

