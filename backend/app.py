# -*- coding: utf-8 -*-
"""
AI 数据分析平台 - FastAPI 主入口
"""
import logging
import time

from fastapi import Depends
from starlette.requests import Request

from backend.admin_auth import admin_required, auth
from backend.app_runtime import RUNTIME_HEADER_NAME, RUNTIME_HEADER_VALUE, create_app
from backend.observability import (
    REQUEST_ID_HEADER,
    bind_request_id,
    current_request_id,
    finish_http_request,
    generate_request_id,
    record_http_request,
    reset_request_id,
    start_http_request,
)
from backend.admin.routes import router as admin_router
from backend.routes.analysis import router as analysis_router
from backend.routes.auth import router as auth_router
from backend.routes.datasets import router as datasets_router
from backend.routes.files import router as files_router
from backend.routes.frontend import mount_frontend_assets, router as frontend_router
from backend.routes.health import router as health_router
from backend.routes.jobs import router as jobs_router
from backend.routes.processing import router as processing_router
from backend.routes.share import router as share_router
from backend.routes.session import router as session_router
from backend.routes.visualization import router as visualization_router

app = create_app()
logger = logging.getLogger("spssgo.http")


def _resolve_path_label(request: Request, fallback: str) -> str:
    """从 request.scope 提取路由 path，未匹配路由时返回 fallback。"""
    route = request.scope.get("route")
    return getattr(route, "path", fallback)


@app.middleware("http")
async def attach_runtime_header(request: Request, call_next):
    request_id = request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
    token = bind_request_id(request_id)
    started = time.perf_counter()
    path_label = request.url.path
    in_progress_metric = start_http_request(request.method)
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        path_label = _resolve_path_label(request, path_label)
        response.headers.setdefault(RUNTIME_HEADER_NAME, RUNTIME_HEADER_VALUE)
        response.headers.setdefault(REQUEST_ID_HEADER, request_id)
        return response
    except Exception:
        path_label = _resolve_path_label(request, path_label)
        duration_seconds = time.perf_counter() - started
        logger.exception(
            "request failed",
            extra={
                "method": request.method,
                "path": path_label,
                "status_code": status_code,
                "duration_ms": round(duration_seconds * 1000, 2),
                "client_ip": request.client.host if request.client else "",
            },
        )
        raise
    finally:
        duration_seconds = time.perf_counter() - started
        finish_http_request(in_progress_metric)
        path_label = _resolve_path_label(request, path_label)
        record_http_request(request.method, path_label, status_code, duration_seconds)
        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": path_label,
                "status_code": status_code,
                "duration_ms": round(duration_seconds * 1000, 2),
                "client_ip": request.client.host if request.client else "",
                "request_id": current_request_id(),
            },
        )
        reset_request_id(token)


secure_dependencies = [Depends(auth.access_token_required)]

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(session_router, dependencies=secure_dependencies)
app.include_router(datasets_router, dependencies=secure_dependencies)
app.include_router(files_router, dependencies=secure_dependencies)
app.include_router(processing_router, dependencies=secure_dependencies)
app.include_router(analysis_router, dependencies=secure_dependencies)
app.include_router(visualization_router, dependencies=secure_dependencies)
app.include_router(jobs_router, dependencies=secure_dependencies)
app.include_router(admin_router, dependencies=secure_dependencies + [Depends(admin_required)])
app.include_router(share_router)
app.include_router(frontend_router)
mount_frontend_assets(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000)
