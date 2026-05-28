# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from backend.config import R_ENABLED, R_EXECUTION_TIMEOUT_SECONDS, RSCRIPT_BIN, R_TEMP_DIR

R_SCRIPTS_DIR = Path(__file__).resolve().parent / "r_scripts"


class RExecutionError(RuntimeError):
    pass


_R_UNICODE_MARKER_RE = re.compile(r"<U\+([0-9A-Fa-f]{4,6})>")


def _decode_r_unicode_markers(value):
    if isinstance(value, str):
        return _R_UNICODE_MARKER_RE.sub(lambda match: chr(int(match.group(1), 16)), value)
    if isinstance(value, list):
        return [_decode_r_unicode_markers(item) for item in value]
    if isinstance(value, dict):
        return {key: _decode_r_unicode_markers(item) for key, item in value.items()}
    return value


def _create_temp_dir() -> Path:
    base_dir = Path(R_TEMP_DIR).expanduser().resolve()
    if any(ord(ch) > 127 for ch in str(base_dir)):
        # Windows Rscript 在非 UTF-8 locale 下读中文临时路径会丢 --input，别让主流程挂。
        base_dir = Path(tempfile.gettempdir()).resolve() / "spssgo-r"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = base_dir / f"spssgo-r-{uuid.uuid4().hex[:10]}"
    temp_dir.mkdir(parents=True, exist_ok=False)
    return temp_dir


def _cleanup_temp_dir(path: Path) -> None:
    try:
        shutil.rmtree(path, ignore_errors=False)
    except Exception:
        # This Windows environment may leave temp dirs locked briefly; cleanup is best-effort.
        pass


def is_r_runtime_available() -> bool:
    if not R_ENABLED:
        return False
    return shutil.which(RSCRIPT_BIN) is not None


def get_r_script_path(script_name: str) -> Path:
    path = (R_SCRIPTS_DIR / script_name).resolve()
    if R_SCRIPTS_DIR not in path.parents:
        raise RExecutionError("非法的 R 脚本路径")
    if not path.exists():
        raise RExecutionError(f"R 脚本不存在: {script_name}")
    return path


def run_r_script(
    script_name: str,
    *,
    payload: dict | None = None,
    temp_files: dict[str, str | bytes] | None = None,
    extra_args: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    if not R_ENABLED:
        raise RExecutionError("R 功能未启用，请先设置 R_ENABLED=1")

    script_path = get_r_script_path(script_name)
    command = [RSCRIPT_BIN, str(script_path)]
    timeout = timeout_seconds or R_EXECUTION_TIMEOUT_SECONDS

    temp_path = _create_temp_dir()
    try:
        if temp_files:
            for filename, content in temp_files.items():
                file_path = (temp_path / filename).resolve()
                if temp_path not in file_path.parents:
                    raise RExecutionError(f"非法的临时文件路径: {filename}")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, bytes):
                    file_path.write_bytes(content)
                else:
                    file_path.write_text(content, encoding="utf-8")
        if payload is not None:
            input_path = temp_path / "input.json"
            input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            command.extend(["--input", str(input_path)])
        if extra_args:
            command.extend(extra_args)
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RExecutionError(f"找不到 Rscript 可执行文件: {RSCRIPT_BIN}") from exc
        except subprocess.TimeoutExpired as exc:
            raise RExecutionError(f"R 脚本执行超时: {script_name}") from exc
    finally:
        _cleanup_temp_dir(temp_path)

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    if completed.returncode != 0:
        detail = stderr or stdout or f"exit code={completed.returncode}"
        raise RExecutionError(f"R 脚本执行失败: {detail}")
    if not stdout:
        return {"success": True, "stdout": "", "stderr": stderr}
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "success": True,
            "stdout": stdout,
            "stderr": stderr,
        }
    if isinstance(parsed, dict):
        return _decode_r_unicode_markers(parsed)
    return {"success": True, "data": _decode_r_unicode_markers(parsed), "stderr": stderr}


def run_r_health_check() -> dict:
    return run_r_script("health_check.R")
