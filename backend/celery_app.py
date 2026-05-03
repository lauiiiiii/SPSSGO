# -*- coding: utf-8 -*-
from __future__ import annotations

from backend.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

try:
    from celery import Celery
except Exception:  # pragma: no cover - optional runtime dependency
    Celery = None


celery_app = None
if Celery is not None:
    celery_app = Celery("spssgo", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Shanghai",
        enable_utc=False,
    )
