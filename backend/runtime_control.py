from __future__ import annotations

import asyncio
import secrets
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import HTTPException, Request

from backend.config import REDIS_URL, SESSION_WRITE_LOCK_TTL_SECONDS

try:
    from redis.asyncio import from_url
except Exception:  # pragma: no cover - optional runtime dependency
    from_url = None


_REDIS_CLIENT = None
_REDIS_DISABLED_UNTIL = 0.0
_REDIS_CLIENT_LOCK = asyncio.Lock()
_RATE_LIMIT_STATE: dict[str, tuple[int, float]] = {}
_RATE_LIMIT_STATE_LOCK = asyncio.Lock()
_LOCAL_SESSION_LOCKS: dict[str, asyncio.Lock] = {}
_LOCK_RELEASE_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int
    count: int


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip
    return (request.client.host if request.client else "") or "unknown"


async def enforce_rate_limit(
    scope: str,
    identifier: str,
    *,
    limit: int,
    window_seconds: int,
    message: str | None = None,
):
    result = await hit_rate_limit(scope, identifier, limit=limit, window_seconds=window_seconds)
    if result.allowed:
        return result
    retry_after = max(result.retry_after, 1)
    detail = message or f"请求过于频繁，请在 {retry_after} 秒后重试"
    raise HTTPException(429, detail)


async def hit_rate_limit(scope: str, identifier: str, *, limit: int, window_seconds: int) -> RateLimitResult:
    safe_scope = _normalize_key_part(scope)
    safe_identifier = _normalize_key_part(identifier)
    window_seconds = max(int(window_seconds), 1)
    limit = max(int(limit), 1)
    now = time.time()
    retry_after = max(1, int(window_seconds - (now % window_seconds)))
    key = f"spssgo:ratelimit:{safe_scope}:{safe_identifier}:{int(now // window_seconds)}"

    client = await get_redis_client()
    if client is not None:
        try:
            count = int(await client.incr(key))
            if count == 1:
                await client.expire(key, window_seconds + 1)
            return RateLimitResult(
                allowed=count <= limit,
                limit=limit,
                remaining=max(limit - count, 0),
                retry_after=retry_after,
                count=count,
            )
        except Exception:
            await _disable_redis_client(client)
            pass

    async with _RATE_LIMIT_STATE_LOCK:
        stored = _RATE_LIMIT_STATE.get(key)
        expires_at = now + window_seconds + 1
        if stored is None or stored[1] <= now:
            count = 1
        else:
            count = stored[0] + 1
        _RATE_LIMIT_STATE[key] = (count, expires_at)
        _cleanup_local_rate_limits(now)
    return RateLimitResult(
        allowed=count <= limit,
        limit=limit,
        remaining=max(limit - count, 0),
        retry_after=retry_after,
        count=count,
    )


@asynccontextmanager
async def session_write_lock(
    session_id: str,
    *,
    holder: str = "",
    ttl_seconds: int | None = None,
    wait_timeout: float | None = None,
    busy_message: str = "当前会话已有写任务正在执行，请稍后重试",
):
    ttl = max(int(ttl_seconds or SESSION_WRITE_LOCK_TTL_SECONDS), 1)
    lock_key = f"spssgo:lock:session-write:{_normalize_key_part(session_id)}"
    token = f"{_normalize_key_part(holder or 'unknown')}:{secrets.token_hex(16)}"
    local_lock = _local_session_lock(session_id)
    client = await get_redis_client()
    acquired_remote = False
    deadline = None if wait_timeout is None else (time.monotonic() + max(wait_timeout, 0.0))

    if client is not None:
        while True:
            try:
                acquired_remote = bool(await client.set(lock_key, token, nx=True, ex=ttl))
            except Exception:
                await _disable_redis_client(client)
                client = None
                break
            if acquired_remote:
                break
            if deadline is not None and time.monotonic() >= deadline:
                raise HTTPException(409, busy_message)
            await asyncio.sleep(0.1)

    acquired_local = False
    try:
        if deadline is None:
            await local_lock.acquire()
            acquired_local = True
        else:
            remaining = max(deadline - time.monotonic(), 0.0)
            if remaining <= 0:
                raise HTTPException(409, busy_message)
            try:
                await asyncio.wait_for(local_lock.acquire(), timeout=remaining)
            except asyncio.TimeoutError as exc:
                raise HTTPException(409, busy_message) from exc
            acquired_local = True
        yield
    finally:
        if acquired_local and local_lock.locked():
            local_lock.release()
        if client is not None and acquired_remote:
            try:
                await client.eval(_LOCK_RELEASE_SCRIPT, 1, lock_key, token)
            except Exception:
                pass


async def get_redis_client():
    global _REDIS_CLIENT
    if from_url is None:
        return None
    if _REDIS_CLIENT is not None:
        return _REDIS_CLIENT
    if time.time() < _REDIS_DISABLED_UNTIL:
        return None

    async with _REDIS_CLIENT_LOCK:
        if _REDIS_CLIENT is not None:
            return _REDIS_CLIENT
        if time.time() < _REDIS_DISABLED_UNTIL:
            return None

        client = from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            health_check_interval=30,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
        )
        try:
            await client.ping()
        except Exception:
            await _disable_redis_client(client)
            return None
        _REDIS_CLIENT = client
        return _REDIS_CLIENT


def _cleanup_local_rate_limits(now: float):
    expired_keys = [key for key, (_, expires_at) in _RATE_LIMIT_STATE.items() if expires_at <= now]
    for key in expired_keys:
        _RATE_LIMIT_STATE.pop(key, None)


async def _disable_redis_client(client=None, *, cooldown_seconds: float = 5.0):
    global _REDIS_CLIENT, _REDIS_DISABLED_UNTIL
    target = client or _REDIS_CLIENT
    _REDIS_CLIENT = None
    _REDIS_DISABLED_UNTIL = time.time() + max(cooldown_seconds, 0.0)
    if target is None:
        return

    closer = getattr(target, "aclose", None) or getattr(target, "close", None)
    if closer is None:
        return
    try:
        result = closer()
        if asyncio.iscoroutine(result):
            await result
    except Exception:
        pass


def _local_session_lock(session_id: str) -> asyncio.Lock:
    lock = _LOCAL_SESSION_LOCKS.get(session_id)
    if lock is None:
        lock = asyncio.Lock()
        _LOCAL_SESSION_LOCKS[session_id] = lock
    return lock


def _normalize_key_part(value: str) -> str:
    return str(value or "unknown").replace(" ", "_").replace(":", "_").replace("/", "_")
