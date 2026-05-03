# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging
import importlib
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

from fastapi.responses import PlainTextResponse

from backend.config import (
    LOG_JSON,
    LOG_LEVEL,
    METRICS_ENABLED,
    SENTRY_DSN,
    SENTRY_ENVIRONMENT,
    SENTRY_TRACES_SAMPLE_RATE,
)

try:  # pragma: no cover - optional dependency in local dev
    sentry_sdk = importlib.import_module("sentry_sdk")
except Exception:  # pragma: no cover
    sentry_sdk = None

try:  # pragma: no cover - optional dependency in local dev
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
except Exception:  # pragma: no cover
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    Counter = Gauge = Histogram = None
    generate_latest = None


REQUEST_ID_HEADER = "X-Request-ID"
_request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
_initialized = False
_logger = logging.getLogger("spssgo")

_STANDARD_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "request_id",
}

_PROMETHEUS_AVAILABLE = bool(Counter and Histogram and Gauge and generate_latest)
_METRICS_AVAILABLE = METRICS_ENABLED and _PROMETHEUS_AVAILABLE

if _METRICS_AVAILABLE:
    HTTP_REQUESTS_TOTAL = Counter(
        "spssgo_http_requests_total",
        "Total HTTP requests.",
        ["method", "path", "status"],
    )
    HTTP_REQUEST_DURATION_SECONDS = Histogram(
        "spssgo_http_request_duration_seconds",
        "HTTP request latency in seconds.",
        ["method", "path"],
        buckets=(0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 5, 10, 30),
    )
    HTTP_REQUESTS_IN_PROGRESS = Gauge(
        "spssgo_http_requests_in_progress",
        "Current HTTP requests in progress grouped by method.",
        ["method"],
    )
    JOB_SUBMISSIONS_TOTAL = Counter(
        "spssgo_job_submissions_total",
        "Submitted jobs grouped by type and queue.",
        ["job_type", "queue"],
    )
    JOB_TRANSITIONS_TOTAL = Counter(
        "spssgo_job_transitions_total",
        "Job lifecycle transitions grouped by type, queue and status.",
        ["job_type", "queue", "status"],
    )
    JOB_DURATION_SECONDS = Histogram(
        "spssgo_job_duration_seconds",
        "Job runtime in seconds grouped by type, queue and final status.",
        ["job_type", "queue", "status"],
        buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300, 900),
    )
    JOBS_RUNNING = Gauge(
        "spssgo_jobs_running",
        "Currently running jobs grouped by type and queue.",
        ["job_type", "queue"],
    )
    SANDBOX_EXECUTIONS_TOTAL = Counter(
        "spssgo_sandbox_executions_total",
        "Sandbox execution outcomes grouped by executor mode and status.",
        ["executor_mode", "status"],
    )
    SANDBOX_DURATION_SECONDS = Histogram(
        "spssgo_sandbox_duration_seconds",
        "Sandbox execution durations grouped by executor mode and status.",
        ["executor_mode", "status"],
        buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120),
    )


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = current_request_id()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", current_request_id()),
        }
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_RECORD_ATTRS and not key.startswith("_")
        }
        if extras:
            payload.update(extras)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def init_observability() -> None:
    global _initialized
    if _initialized:
        return
    _configure_logging()
    _init_sentry()
    _logger.info(
        "observability initialized",
        extra={
            "metrics_enabled": METRICS_ENABLED,
            "metrics_available": _METRICS_AVAILABLE,
            "sentry_enabled": bool(SENTRY_DSN and sentry_sdk is not None),
            "log_json": LOG_JSON,
        },
    )
    _initialized = True


def current_request_id() -> str:
    return _request_id_var.get("-")


def bind_request_id(request_id: str):
    return _request_id_var.set(request_id)


def reset_request_id(token) -> None:
    _request_id_var.reset(token)


def generate_request_id() -> str:
    return uuid.uuid4().hex[:12]


def record_http_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    if not _METRICS_AVAILABLE:
        return
    status = str(status_code)
    HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=status).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(max(0.0, duration_seconds))


def start_http_request(method: str):
    if not _METRICS_AVAILABLE:
        return None
    child = HTTP_REQUESTS_IN_PROGRESS.labels(method=method)
    child.inc()
    return child


def finish_http_request(metric_handle) -> None:
    if metric_handle is None:
        return
    try:
        metric_handle.dec()
    except Exception:
        pass


def record_job_submission(job_type: str, queue: str) -> None:
    if not _METRICS_AVAILABLE:
        return
    JOB_SUBMISSIONS_TOTAL.labels(job_type=job_type, queue=queue).inc()


def record_job_transition(job_type: str, queue: str, status: str) -> None:
    if not _METRICS_AVAILABLE:
        return
    JOB_TRANSITIONS_TOTAL.labels(job_type=job_type, queue=queue, status=status).inc()


def start_job_execution(job_type: str, queue: str):
    if not _METRICS_AVAILABLE:
        return None
    child = JOBS_RUNNING.labels(job_type=job_type, queue=queue)
    child.inc()
    return child


def finish_job_execution(metric_handle, job_type: str, queue: str, status: str, duration_seconds: float | None = None) -> None:
    if metric_handle is not None:
        try:
            metric_handle.dec()
        except Exception:
            pass
    if not _METRICS_AVAILABLE:
        return
    if duration_seconds is not None:
        JOB_DURATION_SECONDS.labels(job_type=job_type, queue=queue, status=status).observe(max(0.0, duration_seconds))


def record_sandbox_execution(executor_mode: str | None, status: str, duration_seconds: float | None = None) -> None:
    if not _METRICS_AVAILABLE:
        return
    mode = (executor_mode or "unknown").lower()
    SANDBOX_EXECUTIONS_TOTAL.labels(executor_mode=mode, status=status).inc()
    if duration_seconds is not None:
        SANDBOX_DURATION_SECONDS.labels(executor_mode=mode, status=status).observe(max(0.0, duration_seconds))


def metrics_response():
    if not METRICS_ENABLED:
        return PlainTextResponse("metrics disabled\n", status_code=404)
    if not _PROMETHEUS_AVAILABLE or generate_latest is None:
        return PlainTextResponse("prometheus_client not installed\n", status_code=503)
    payload = generate_latest()
    return PlainTextResponse(payload.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


def _configure_logging() -> None:
    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    if LOG_JSON:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s"
            )
        )
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True


def _init_sentry() -> None:
    if not SENTRY_DSN:
        return
    if sentry_sdk is None:
        _logger.warning("sentry_sdk not installed; sentry disabled")
        return
    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
            environment=SENTRY_ENVIRONMENT,
        )
    except Exception as exc:  # pragma: no cover - defensive init path
        _logger.warning("failed to initialize sentry", extra={"error": str(exc)})
