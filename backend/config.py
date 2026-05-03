# -*- coding: utf-8 -*-
"""项目运行时配置集中入口，别把业务逻辑和密钥默认值塞进来。"""
from __future__ import annotations

import os
import secrets
import string
import tempfile
import warnings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)


# 开发环境用安全随机值替代硬编码密码
# 值固定到进程生命周期，避免同一次启动内前后不一致
_DEV_PASSWORD_CACHE: dict[str, str] = {}


def _generate_dev_password(length: int = 16) -> str:
    """生成安全随机密码，开发环境兜底用。"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _dev_password(name: str) -> str:
    """获取开发环境随机密码，同一名称在同进程中缓存。"""
    if name not in _DEV_PASSWORD_CACHE:
        _DEV_PASSWORD_CACHE[name] = _generate_dev_password()
    return _DEV_PASSWORD_CACHE[name]


def _load_dotenv_file(path: str) -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            if "=" not in line:
                continue

            name, value = line.split("=", 1)
            name = name.strip()
            if not name or name in os.environ:
                continue

            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            os.environ[name] = value


_load_dotenv_file(os.path.join(PROJECT_ROOT, ".env"))

APP_ENV = (os.environ.get("APP_ENV") or os.environ.get("ENVIRONMENT") or "development").strip().lower()
IS_DEVELOPMENT = APP_ENV in {"development", "dev", "local", "test"}
ALLOW_INSECURE_DEV_DEFAULTS = os.environ.get(
    "ALLOW_INSECURE_DEV_DEFAULTS",
    "1" if IS_DEVELOPMENT else "0",
) == "1"

_CONFIG_WARNINGS: list[str] = []
_VALIDATION_CACHE: bool = False


def _env(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip()


def _int_env(name: str, default: int) -> int:
    return int(_env(name, str(default)))


def _float_env(name: str, default: float) -> float:
    return float(_env(name, str(default)))


def _bool_env(name: str, default: bool) -> bool:
    return _env(name, "1" if default else "0") == "1"


def _csv_env(name: str, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    raw = _env(name, ",".join(default))
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _dev_default(name: str, value: str) -> str:
    if ALLOW_INSECURE_DEV_DEFAULTS:
        _CONFIG_WARNINGS.append(f"{name} 使用了本地开发默认值，仅适用于开发环境")
        return value
    return ""


def _secure_dev_default(name: str, fallback: str | None = None) -> str:
    """开发环境敏感配置兜底：优先随机生成，仅当显式允许时才用传入值。"""
    if not ALLOW_INSECURE_DEV_DEFAULTS:
        return ""
    _CONFIG_WARNINGS.append(f"{name} 使用了本地开发默认值，仅适用于开发环境")
    if fallback is not None:
        return fallback
    return _dev_password(name)


DEEPSEEK_API_KEY = _env("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = _env("DEEPSEEK_MODEL", "deepseek-chat")

STORAGE_BACKEND = _env("STORAGE_BACKEND", "local")
LOCAL_STORAGE_ROOT = _env("LOCAL_STORAGE_ROOT", os.path.join(PROJECT_ROOT, ".data"))
S3_ENDPOINT_URL = _env("S3_ENDPOINT_URL", "")
S3_REGION = _env("S3_REGION", "")
S3_BUCKET = _env("S3_BUCKET", "")
S3_ACCESS_KEY = _env("S3_ACCESS_KEY", "")
S3_SECRET_KEY = _env("S3_SECRET_KEY", "")
S3_KEY_PREFIX = _env("S3_KEY_PREFIX", "")

JOB_BACKEND = _env("JOB_BACKEND", "local").lower()
CELERY_BROKER_URL = _env("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = _env("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")

SESSION_WRITE_LOCK_TTL_SECONDS = _int_env("SESSION_WRITE_LOCK_TTL_SECONDS", 1800)
LOGIN_RATE_LIMIT_COUNT = _int_env("LOGIN_RATE_LIMIT_COUNT", 10)
LOGIN_RATE_LIMIT_WINDOW_SECONDS = _int_env("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 60)
UPLOAD_RATE_LIMIT_COUNT = _int_env("UPLOAD_RATE_LIMIT_COUNT", 20)
UPLOAD_RATE_LIMIT_WINDOW_SECONDS = _int_env("UPLOAD_RATE_LIMIT_WINDOW_SECONDS", 300)
AI_PLAN_RATE_LIMIT_COUNT = _int_env("AI_PLAN_RATE_LIMIT_COUNT", 8)
AI_PLAN_RATE_LIMIT_WINDOW_SECONDS = _int_env("AI_PLAN_RATE_LIMIT_WINDOW_SECONDS", 300)
AI_INTERPRET_RATE_LIMIT_COUNT = _int_env("AI_INTERPRET_RATE_LIMIT_COUNT", 20)
AI_INTERPRET_RATE_LIMIT_WINDOW_SECONDS = _int_env("AI_INTERPRET_RATE_LIMIT_WINDOW_SECONDS", 300)
FAULT_INJECTION_JOB_DELAY_SECONDS = _float_env("FAULT_INJECTION_JOB_DELAY_SECONDS", 0.0)
FAULT_INJECTION_JOB_DELAY_TYPES = tuple(
    item.strip().lower()
    for item in _env("FAULT_INJECTION_JOB_DELAY_TYPES", "").split(",")
    if item.strip()
)

DB_AUTO_CREATE = _bool_env("DB_AUTO_CREATE", ALLOW_INSECURE_DEV_DEFAULTS)
LOG_LEVEL = _env("LOG_LEVEL", "INFO").upper()
LOG_JSON = _bool_env("LOG_JSON", True)
METRICS_ENABLED = _bool_env("METRICS_ENABLED", True)
SENTRY_DSN = _env("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = _env("SENTRY_ENVIRONMENT", APP_ENV)
SENTRY_TRACES_SAMPLE_RATE = _float_env("SENTRY_TRACES_SAMPLE_RATE", 0.0)
CORS_ALLOW_ORIGINS = _csv_env(
    "CORS_ALLOW_ORIGINS",
    (
        "http://localhost:5577",
        "http://127.0.0.1:5577",
        "http://localhost:5578",
        "http://127.0.0.1:5578",
    ),
)

SANDBOX_DOCKER_ENABLED = _bool_env("SANDBOX_DOCKER_ENABLED", False)
SANDBOX_DOCKER_BIN = _env("SANDBOX_DOCKER_BIN", "docker")
SANDBOX_DOCKER_IMAGE = _env("SANDBOX_DOCKER_IMAGE", "")
SANDBOX_DOCKER_MEMORY_LIMIT = _env("SANDBOX_DOCKER_MEMORY_LIMIT", "768m")
SANDBOX_DOCKER_CPUS = _env("SANDBOX_DOCKER_CPUS", "1.0")
SANDBOX_DOCKER_PIDS_LIMIT = _int_env("SANDBOX_DOCKER_PIDS_LIMIT", 128)
SANDBOX_CONTAINER_USER = _env("SANDBOX_CONTAINER_USER", "65534:65534")
SANDBOX_WORKSPACE_SIZE = _env("SANDBOX_WORKSPACE_SIZE", "256m")
SANDBOX_TMP_SIZE = _env("SANDBOX_TMP_SIZE", "128m")
SANDBOX_SHARED_STORAGE_VOLUME = _env("SANDBOX_SHARED_STORAGE_VOLUME", "")
SANDBOX_SHARED_STORAGE_TARGET = _env("SANDBOX_SHARED_STORAGE_TARGET", LOCAL_STORAGE_ROOT)
R_ENABLED = _bool_env("R_ENABLED", False)
RSCRIPT_BIN = _env("RSCRIPT_BIN", "Rscript")
R_EXECUTION_TIMEOUT_SECONDS = _int_env("R_EXECUTION_TIMEOUT_SECONDS", 120)
R_TEMP_DIR = _env("R_TEMP_DIR", os.path.join(tempfile.gettempdir(), "spssgo-r"))

# MySQL
MYSQL_HOST = _env("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = _int_env("MYSQL_PORT", 3306)
MYSQL_USER = _env("MYSQL_USER", "root")
MYSQL_PASSWORD = _env("MYSQL_PASSWORD", "") or _secure_dev_default("MYSQL_PASSWORD")
MYSQL_DATABASE = _env("MYSQL_DATABASE", "data_analysis")
MYSQL_POOL_MINSIZE = _int_env("MYSQL_POOL_MINSIZE", 4)
MYSQL_POOL_MAXSIZE = _int_env("MYSQL_POOL_MAXSIZE", 50)

MAX_UPLOAD_SIZE_MB = 50
MAX_EXECUTION_SECONDS = 60
MAX_MEMORY_MB = 512
MAX_CONCURRENT_TASKS = 4
SESSION_EXPIRE_HOURS = _int_env("SESSION_EXPIRE_HOURS", 24 * 30)

DATA_EXTENSIONS = {".xlsx", ".xls", ".csv", ".sav", ".zsav", ".dta", ".sas7bdat", ".xpt", ".tsv", ".txt", ".json", ".parquet"}
DOC_EXTENSIONS = {".docx", ".doc"}
ALLOWED_EXTENSIONS = DATA_EXTENSIONS | DOC_EXTENSIONS

# Admin
ADMIN_USERNAME = _env("ADMIN_USERNAME", "") or _dev_default("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = _env("ADMIN_PASSWORD", "") or _secure_dev_default("ADMIN_PASSWORD")
ADMIN_SECRET_KEY = _env("ADMIN_SECRET_KEY", "") or _secure_dev_default("ADMIN_SECRET_KEY")

PYTHON_WHITELIST_MODULES = {
    "pandas", "numpy", "scipy", "statsmodels", "pingouin",
    "factor_analyzer", "sklearn", "math", "statistics",
    "json", "collections", "itertools", "functools",
}

PYTHON_BLACKLIST_PATTERNS = [
    "import os", "import sys", "import subprocess", "import shutil",
    "import socket", "import http", "import urllib",
    "__import__", "exec(", "eval(", "compile(",
    "open(", "os.system", "os.popen",
]


def validate_runtime_config() -> None:
    global _VALIDATION_CACHE
    if _VALIDATION_CACHE:
        return

    errors: list[str] = []
    if not MYSQL_PASSWORD:
        errors.append("必须配置 MYSQL_PASSWORD")
    if not ADMIN_USERNAME:
        errors.append("必须配置 ADMIN_USERNAME")
    if not ADMIN_PASSWORD:
        errors.append("必须配置 ADMIN_PASSWORD")
    if not ADMIN_SECRET_KEY:
        errors.append("必须配置 ADMIN_SECRET_KEY")
    if SANDBOX_DOCKER_ENABLED and not SANDBOX_DOCKER_IMAGE:
        errors.append("启用 SANDBOX_DOCKER_ENABLED=1 时必须配置 SANDBOX_DOCKER_IMAGE")

    if not IS_DEVELOPMENT:
        if ALLOW_INSECURE_DEV_DEFAULTS:
            errors.append("非开发环境不能启用 ALLOW_INSECURE_DEV_DEFAULTS=1")
        if DB_AUTO_CREATE:
            errors.append("非开发环境禁止启用 DB_AUTO_CREATE=1，请使用 Alembic 迁移")

    if errors:
        detail = "\n".join(f"- {item}" for item in errors)
        raise RuntimeError(f"运行时配置不合法:\n{detail}")

    if _CONFIG_WARNINGS:
        warnings.warn(
            "当前运行使用了开发环境兜底配置：\n" + "\n".join(f"- {item}" for item in _CONFIG_WARNINGS),
            RuntimeWarning,
            stacklevel=2,
        )

    _VALIDATION_CACHE = True
