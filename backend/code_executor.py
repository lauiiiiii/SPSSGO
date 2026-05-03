# -*- coding: utf-8 -*-
"""
安全沙箱：支持本地子进程执行，以及可选的 Docker 容器隔离执行。
"""
from __future__ import annotations

import json
import os
import posixpath
import shutil
import subprocess
import sys
import uuid

from backend.code_executor_result import parse_execution_result, trim_output
from backend.code_executor_safety import check_code_safety
from backend.code_executor_script import write_wrapper_script
from backend.config import (
    LOCAL_STORAGE_ROOT,
    MAX_EXECUTION_SECONDS,
    SANDBOX_CONTAINER_USER,
    SANDBOX_DOCKER_BIN,
    SANDBOX_DOCKER_CPUS,
    SANDBOX_DOCKER_ENABLED,
    SANDBOX_DOCKER_IMAGE,
    SANDBOX_DOCKER_MEMORY_LIMIT,
    SANDBOX_DOCKER_PIDS_LIMIT,
    SANDBOX_SHARED_STORAGE_TARGET,
    SANDBOX_SHARED_STORAGE_VOLUME,
    SANDBOX_TMP_SIZE,
    SANDBOX_WORKSPACE_SIZE,
    STORAGE_BACKEND,
)


def execute_analysis_code(code: str, data_filepath: str) -> dict:
    """
    执行 AI 生成的分析代码。

    代码必须将结果写入 RESULT 变量（list of dict），每个 dict 包含：
      - name: 分析名称
      - headers: 表头列表
      - rows: 数据行列表（list of list）
      - description: 文字描述
    """
    safe, reason = check_code_safety(code)
    if not safe:
        return {"success": False, "error": reason, "results": []}

    if SANDBOX_DOCKER_ENABLED:
        return _execute_in_container(code, data_filepath)
    return _execute_locally(code, data_filepath)


def _execute_locally(code: str, data_filepath: str) -> dict:
    script_path = write_wrapper_script(code, data_filepath)
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=MAX_EXECUTION_SECONDS,
            cwd=os.path.dirname(data_filepath) or None,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        return parse_execution_result(
            result.stdout,
            result.stderr,
            result.returncode,
            audit={
                "executor_mode": "local",
                "docker_image": "",
                "container_name": "",
                "exit_code": result.returncode,
                "data_strategy": "direct_file",
            },
        )
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"代码执行超时（>{MAX_EXECUTION_SECONDS}秒）",
            "results": [],
            "audit": {
                "executor_mode": "local",
                "docker_image": "",
                "container_name": "",
                "exit_code": None,
                "data_strategy": "direct_file",
            },
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "results": [],
            "audit": {
                "executor_mode": "local",
                "docker_image": "",
                "container_name": "",
                "exit_code": None,
                "data_strategy": "direct_file",
            },
        }
    finally:
        _remove_temp_file(script_path)


def _execute_in_container(code: str, data_filepath: str) -> dict:
    if not SANDBOX_DOCKER_IMAGE:
        return {
            "success": False,
            "error": "Sandbox 已启用容器模式，但未配置 SANDBOX_DOCKER_IMAGE",
            "results": [],
        }
    if shutil.which(SANDBOX_DOCKER_BIN) is None:
        return {
            "success": False,
            "error": f"找不到 Docker 命令: {SANDBOX_DOCKER_BIN}",
            "results": [],
        }

    container_name = f"spssgo-sandbox-{uuid.uuid4().hex[:12]}"
    container_data_path = _resolve_container_data_path(data_filepath)
    needs_data_copy = container_data_path is None
    if container_data_path is None:
        container_data_path = f"/workspace/input/{os.path.basename(data_filepath)}"
    data_strategy = "copied_file" if needs_data_copy else "shared_storage"

    script_path = write_wrapper_script(code, container_data_path)
    try:
        bootstrap = (
            "import pathlib, time; "
            "pathlib.Path('/workspace/input').mkdir(parents=True, exist_ok=True); "
            "time.sleep(3600)"
        )
        run_command = [
            SANDBOX_DOCKER_BIN,
            "run",
            "--detach",
            "--name",
            container_name,
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--pids-limit",
            str(SANDBOX_DOCKER_PIDS_LIMIT),
            "--memory",
            SANDBOX_DOCKER_MEMORY_LIMIT,
            "--cpus",
            str(SANDBOX_DOCKER_CPUS),
            "--user",
            SANDBOX_CONTAINER_USER,
            "--tmpfs",
            f"/tmp:size={SANDBOX_TMP_SIZE},exec,mode=1777",
            "--tmpfs",
            f"/workspace:size={SANDBOX_WORKSPACE_SIZE},exec,mode=1777",
            "-e",
            "PYTHONIOENCODING=utf-8",
            "-e",
            "HOME=/tmp",
            "-e",
            "TMPDIR=/tmp",
            "-e",
            "OMP_NUM_THREADS=1",
            "-e",
            "OPENBLAS_NUM_THREADS=1",
            "-e",
            "MKL_NUM_THREADS=1",
            "-e",
            "NUMEXPR_NUM_THREADS=1",
        ]
        if SANDBOX_SHARED_STORAGE_VOLUME and _is_path_in_local_storage(data_filepath):
            run_command.extend(
                [
                    "--mount",
                    (
                        "type=volume,"
                        f"src={SANDBOX_SHARED_STORAGE_VOLUME},"
                        f"target={SANDBOX_SHARED_STORAGE_TARGET},readonly"
                    ),
                ]
            )
        run_command.extend(
            [
                SANDBOX_DOCKER_IMAGE,
                "python",
                "-c",
                bootstrap,
            ]
        )

        create_result = _run_subprocess(run_command, timeout=30)
        if create_result.returncode != 0:
            return {
                "success": False,
                "error": f"启动 sandbox 容器失败: {trim_output(create_result.stderr or create_result.stdout)}",
                "results": [],
            }

        script_copy = _run_subprocess(
            [
                SANDBOX_DOCKER_BIN,
                "cp",
                script_path,
                f"{container_name}:/workspace/run_analysis.py",
            ],
            timeout=30,
        )
        if script_copy.returncode != 0:
            return {
                "success": False,
                "error": f"复制执行脚本到 sandbox 容器失败: {trim_output(script_copy.stderr or script_copy.stdout)}",
                "results": [],
            }

        if needs_data_copy:
            data_copy = _run_subprocess(
                [
                    SANDBOX_DOCKER_BIN,
                    "cp",
                    data_filepath,
                    f"{container_name}:{container_data_path}",
                ],
                timeout=max(MAX_EXECUTION_SECONDS, 30),
            )
            if data_copy.returncode != 0:
                return {
                    "success": False,
                    "error": f"复制数据文件到 sandbox 容器失败: {trim_output(data_copy.stderr or data_copy.stdout)}",
                    "results": [],
                }

        exec_result = _run_subprocess(
            [
                SANDBOX_DOCKER_BIN,
                "exec",
                container_name,
                "python",
                "/workspace/run_analysis.py",
            ],
            timeout=MAX_EXECUTION_SECONDS + 5,
        )
        return parse_execution_result(
            exec_result.stdout,
            exec_result.stderr,
            exec_result.returncode,
            audit={
                "executor_mode": "docker",
                "docker_image": SANDBOX_DOCKER_IMAGE,
                "container_name": container_name,
                "exit_code": exec_result.returncode,
                "data_strategy": data_strategy,
                "shared_storage_target": SANDBOX_SHARED_STORAGE_TARGET if not needs_data_copy else "",
            },
        )
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Sandbox 容器执行超时（>{MAX_EXECUTION_SECONDS}秒）",
            "results": [],
            "audit": {
                "executor_mode": "docker",
                "docker_image": SANDBOX_DOCKER_IMAGE,
                "container_name": container_name,
                "exit_code": None,
                "data_strategy": data_strategy,
            },
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "results": [],
            "audit": {
                "executor_mode": "docker",
                "docker_image": SANDBOX_DOCKER_IMAGE,
                "container_name": container_name,
                "exit_code": None,
                "data_strategy": data_strategy,
            },
        }
    finally:
        _remove_temp_file(script_path)
        _cleanup_container(container_name)


def _run_subprocess(command: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def _resolve_container_data_path(data_filepath: str) -> str | None:
    if not SANDBOX_SHARED_STORAGE_VOLUME or not _is_path_in_local_storage(data_filepath):
        return None

    local_root = os.path.abspath(LOCAL_STORAGE_ROOT)
    file_path = os.path.abspath(data_filepath)
    try:
        relative = os.path.relpath(file_path, local_root)
    except ValueError:
        return None

    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
        return None

    return posixpath.join(
        SANDBOX_SHARED_STORAGE_TARGET.rstrip("/"),
        relative.replace(os.sep, "/"),
    )


def _is_path_in_local_storage(data_filepath: str) -> bool:
    if STORAGE_BACKEND.lower() != "local":
        return False

    local_root = os.path.abspath(LOCAL_STORAGE_ROOT)
    file_path = os.path.abspath(data_filepath)
    try:
        relative = os.path.relpath(file_path, local_root)
    except ValueError:
        return False
    return relative != os.pardir and not relative.startswith(os.pardir + os.sep)


def _cleanup_container(container_name: str) -> None:
    try:
        _run_subprocess(
            [
                SANDBOX_DOCKER_BIN,
                "rm",
                "--force",
                "--volumes",
                container_name,
            ],
            timeout=15,
        )
    except Exception:
        pass


def _remove_temp_file(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass
