# -*- coding: utf-8 -*-
"""
应用运行时与 FastAPI 装配辅助
"""
import base64
import io
import os
import re
import unicodedata
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.admin_auth import setup_auth
from backend.config import CORS_ALLOW_ORIGINS, validate_runtime_config
from backend.database import close_db, init_db
from backend.observability import init_observability
from backend.openapi_docs import OPENAPI_DESCRIPTION, OPENAPI_TAGS, install_openapi_docs
from backend.storage import storage_service

executor = None

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")
FRONTEND_ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, "assets")


def frontend_file(*parts: str) -> str:
    return os.path.join(FRONTEND_DIST_DIR, *parts)


def _decode_runtime_chunk(values: tuple[int, ...], salt: int) -> str:
    return "".join(chr(value ^ salt) for value in values)


RUNTIME_HEADER_NAME = _decode_runtime_chunk(
    (93, 40, 68, 117, 117, 40, 70, 106, 107, 99, 108, 98),
    5,
)
RUNTIME_HEADER_VALUE = base64.urlsafe_b64encode(
    (
        _decode_runtime_chunk((91, 64, 83, 65, 72, 70, 41), 9)
        + _decode_runtime_chunk((67, 113, 101, 106, 99, 112, 101, 109), 4)
        + _decode_runtime_chunk((108, 111, 103, 110, 99, 40, 38, 71, 106, 106, 38), 6)
        + _decode_runtime_chunk((113, 106, 100, 107, 119, 112, 35, 113, 102, 112, 102, 113, 117, 102, 103), 3)
    ).encode("utf-8")
).decode("ascii").rstrip("=")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_observability()
    validate_runtime_config()
    await init_db()
    storage_service.initialize()
    yield
    await close_db()
    if executor is not None:
        executor.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(
        title="SPSSGO 数据分析平台 API",
        description=OPENAPI_DESCRIPTION,
        version="1.0.0",
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )
    install_openapi_docs(app)
    setup_auth(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(CORS_ALLOW_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def get_executor() -> ProcessPoolExecutor:
    global executor
    if executor is None:
        executor = ProcessPoolExecutor(max_workers=4)
    return executor


def _ascii_download_name(filename: str) -> str:
    """生成 ASCII 兜底文件名，别把中文直接塞 header 里。"""
    raw_name = os.path.basename((filename or "").strip()) or "download"
    stem, ext = os.path.splitext(raw_name)
    normalized_stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", normalized_stem).strip("._-") or "download"
    safe_ext = re.sub(r"[^A-Za-z0-9.]+", "", ext)
    return f"{safe_stem}{safe_ext}"


def _build_download_headers(filename: str) -> dict[str, str]:
    """统一下载头编码，兼容中文文件名和老浏览器。"""
    raw_name = os.path.basename((filename or "").strip()) or "download"
    fallback_name = _ascii_download_name(raw_name)
    encoded_name = quote(raw_name, safe="!#$&+-.^_`|~")
    return {
        "Content-Disposition": f"""attachment; filename="{fallback_name}"; filename*=UTF-8''{encoded_name}""",
    }


def download_response(content: bytes, filename: str, media_type: str):
    headers = _build_download_headers(filename)
    return StreamingResponse(io.BytesIO(content), media_type=media_type, headers=headers)

