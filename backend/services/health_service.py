# -*- coding: utf-8 -*-
"""健康检查服务层，负责基础设施探测编排，别把路由响应细节扩散到别处。"""
from __future__ import annotations

import asyncio
import time

from fastapi.responses import JSONResponse

from backend.config import JOB_BACKEND, REDIS_URL, STORAGE_BACKEND
from backend.database import ping_db
from backend.storage import storage_service


async def get_liveness_payload() -> dict:
    return {
        "status": "ok",
        "service": "spssgo",
        "timestamp": time.time(),
    }


async def get_readiness_response() -> JSONResponse:
    db_ok = await ping_db()
    redis_check = await _ping_redis_if_needed()
    storage_check = await _ping_storage()
    redis_ok = redis_check.get("ok", True)
    storage_ok = storage_check.get("ok", True)
    overall_ok = db_ok and redis_ok and storage_ok
    payload = {
        "status": "ready" if overall_ok else "degraded",
        "timestamp": time.time(),
        "checks": {
            "database": {"ok": db_ok},
            "storage": storage_check,
            "jobs": {"ok": True, "backend": JOB_BACKEND},
            "redis": redis_check,
        },
    }
    return JSONResponse(payload, status_code=200 if overall_ok else 503)


async def _ping_redis_if_needed():
    if JOB_BACKEND != "celery":
        return {"ok": True, "enabled": False, "detail": "local job backend"}
    try:
        from redis.asyncio import from_url
    except Exception:
        return {"ok": False, "enabled": True, "detail": "redis client unavailable"}

    client = from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        pong = await client.ping()
        return {"ok": bool(pong), "enabled": True}
    except Exception as exc:
        return {"ok": False, "enabled": True, "detail": str(exc)}
    finally:
        try:
            await client.aclose()
        except Exception:
            pass


async def _ping_storage():
    try:
        result = await _run_blocking_storage_healthcheck()
        if "backend" not in result:
            result["backend"] = STORAGE_BACKEND
        return result
    except Exception as exc:
        return {"ok": False, "backend": STORAGE_BACKEND, "detail": str(exc)}


async def _run_blocking_storage_healthcheck():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, storage_service.healthcheck)
