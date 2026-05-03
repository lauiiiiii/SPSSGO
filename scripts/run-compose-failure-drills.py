from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.smoke_async_flow import (  # noqa: E402
    ACTIVE_JOB_STATUSES,
    cleanup_session,
    create_session,
    fetch_results,
    login_user,
    request_json,
    submit_execute_method_job,
    submit_upload_job,
    wait_for_job,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run compose failure drills against the async SPSSGO flow.")
    parser.add_argument("--base-url", default=os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--compose-file", default="compose.yaml")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--username", default=os.environ.get("SMOKE_USERNAME") or os.environ.get("ADMIN_USERNAME", "admin"))
    parser.add_argument("--password", default=os.environ.get("SMOKE_PASSWORD") or os.environ.get("ADMIN_PASSWORD", ""))
    parser.add_argument(
        "--csv-path",
        default=os.path.join(PROJECT_ROOT, "loadtests", "fixtures", "category_summary_sample.csv"),
    )
    parser.add_argument("--job-timeout", type=int, default=int(os.environ.get("SMOKE_JOB_TIMEOUT", "120")))
    parser.add_argument("--poll-interval", type=float, default=float(os.environ.get("SMOKE_POLL_INTERVAL", "1.0")))
    parser.add_argument("--restart-delay", type=float, default=0.5)
    parser.add_argument("--api-service", default="api")
    parser.add_argument("--worker-service", default="worker-analysis")
    parser.add_argument("--redis-service", default="redis")
    parser.add_argument("--drills", default="api,worker,redis")
    parser.add_argument("--start-stack", action="store_true")
    parser.add_argument("--down-after", action="store_true")
    parser.add_argument(
        "--report-path",
        default=os.path.join(PROJECT_ROOT, "acceptance_refs", "validation", "compose_failure_drill_record.md"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.password:
        raise SystemExit("Missing --password or ADMIN_PASSWORD/SMOKE_PASSWORD environment variable")
    if not os.path.exists(args.csv_path):
        raise SystemExit(f"Fixture file not found: {args.csv_path}")

    drills = [item.strip().lower() for item in args.drills.split(",") if item.strip()]
    compose_args = compose_base_args(args.compose_file, args.env_file)
    results: list[dict[str, Any]] = []

    if args.start_stack:
        print("[failure-drills] starting compose stack...")
        run_command([*compose_args, "up", "-d", "--build"])

    try:
        wait_ready(args.base_url, timeout_seconds=300)
        for drill in drills:
            if drill == "api":
                results.append(run_api_restart_drill(args, compose_args))
            elif drill == "worker":
                results.append(run_worker_restart_drill(args, compose_args))
            elif drill == "redis":
                results.append(run_redis_restart_drill(args, compose_args))
            else:
                raise RuntimeError(f"Unsupported drill name: {drill}")
    finally:
        if args.down_after:
            print("[failure-drills] stopping compose stack...")
            run_command([*compose_args, "down"], check=False)

    report_text = render_report(args.base_url, results)
    if args.report_path:
        os.makedirs(os.path.dirname(args.report_path), exist_ok=True)
        with open(args.report_path, "w", encoding="utf-8") as handle:
            handle.write(report_text)
        print(f"[failure-drills] report written: {args.report_path}")

    failed = [item for item in results if not item.get("passed")]
    if failed:
        for item in failed:
            print(f"[failure-drills] failed: {item['name']} -> {item.get('error') or 'unknown error'}", file=sys.stderr)
        return 1

    print("[failure-drills] all drills passed")
    return 0


def compose_base_args(compose_file: str, env_file: str) -> list[str]:
    args = ["docker", "compose", "-f", compose_file]
    if env_file and os.path.exists(env_file):
        args.extend(["--env-file", env_file])
    return args


def run_command(args: list[str], *, check: bool = True, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit={completed.returncode}"
        raise RuntimeError(f"Command failed: {' '.join(args)} -> {detail}")
    return completed


def wait_ready(base_url: str, *, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            response = request_json("GET", f"{base_url.rstrip('/')}/api/health/ready")
            if response["status"] == 200:
                return
            last_error = f"{response['status']} {response['text']}"
        except Exception as exc:  # pragma: no cover - transient during restart
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"Timed out waiting for readiness: {last_error}")


def wait_for_job_resilient(
    base_url: str,
    job_id: str,
    headers: dict[str, str],
    *,
    timeout_seconds: int,
    poll_interval: float,
    transient_error_budget: int = 10,
) -> dict[str, Any]:
    started = time.time()
    transient_errors = 0
    while time.time() - started < timeout_seconds:
        response = request_json("GET", f"{base_url.rstrip('/')}/api/jobs/{job_id}", headers=headers)
        if response["status"] != 200:
            transient_errors += 1
            if transient_errors > transient_error_budget:
                raise RuntimeError(f"job status failed for {job_id}: {response['status']} {response['text']}")
            time.sleep(poll_interval)
            continue

        transient_errors = 0
        payload = response["json"]
        status = (payload.get("status") or "").lower()
        if status not in ACTIVE_JOB_STATUSES:
            if status != "succeeded":
                raise RuntimeError(f"job {job_id} ended as {status}: {payload.get('error_message') or ''}")
            return payload
        time.sleep(poll_interval)
    raise RuntimeError(f"job {job_id} timed out after {timeout_seconds}s")


def prepare_execute_job(args: argparse.Namespace) -> dict[str, Any]:
    base_url = args.base_url.rstrip("/")
    headers = login_user(base_url, args.username, args.password)
    session_id = create_session(base_url, headers)
    upload_job_id = submit_upload_job(base_url, session_id, args.csv_path, headers)
    upload_job = wait_for_job(base_url, upload_job_id, headers, args.job_timeout, args.poll_interval)
    execute_job_id = submit_execute_method_job(
        base_url,
        session_id,
        headers,
        method="category_summary",
        group_var="group",
        summary_vars=["score_a", "score_b"],
    )
    return {
        "headers": headers,
        "session_id": session_id,
        "upload_job_id": upload_job_id,
        "upload_job": upload_job,
        "execute_job_id": execute_job_id,
    }


def finalize_execute_job(args: argparse.Namespace, probe: dict[str, Any]) -> dict[str, Any]:
    base_url = args.base_url.rstrip("/")
    job = wait_for_job_resilient(
        base_url,
        probe["execute_job_id"],
        probe["headers"],
        timeout_seconds=args.job_timeout,
        poll_interval=args.poll_interval,
    )
    results = fetch_results(base_url, probe["session_id"], probe["headers"])
    matched = [item for item in results if item.get("job_id") == probe["execute_job_id"]]
    if not matched:
        raise RuntimeError("execute-method job finished, but no result rows were found")
    return {
        "job": job,
        "matched_results": len(matched),
    }


def cleanup_probe(args: argparse.Namespace, probe: dict[str, Any]) -> None:
    if not probe:
        return
    try:
        cleanup_session(args.base_url.rstrip("/"), probe["session_id"], probe["headers"])
    except Exception:
        pass


def run_api_restart_drill(args: argparse.Namespace, compose_args: list[str]) -> dict[str, Any]:
    result = {"name": "api_restart", "service": args.api_service, "passed": False}
    probe: dict[str, Any] | None = None
    try:
        probe = prepare_execute_job(args)
        time.sleep(max(args.restart_delay, 0.0))
        restart_started = time.time()
        run_command([*compose_args, "restart", args.api_service], timeout=300)
        wait_ready(args.base_url, timeout_seconds=300)
        finalized = finalize_execute_job(args, probe)
        result.update(
            passed=True,
            restart_seconds=round(time.time() - restart_started, 2),
            execute_job_id=probe["execute_job_id"],
            dataset_version_id=finalized["job"].get("dataset_version_id"),
            matched_results=finalized["matched_results"],
        )
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result
    finally:
        cleanup_probe(args, probe)


def run_worker_restart_drill(args: argparse.Namespace, compose_args: list[str]) -> dict[str, Any]:
    result = {"name": "worker_restart", "service": args.worker_service, "passed": False}
    probe: dict[str, Any] | None = None
    try:
        probe = prepare_execute_job(args)
        time.sleep(max(args.restart_delay, 0.0))
        restart_started = time.time()
        run_command([*compose_args, "restart", args.worker_service], timeout=300)
        finalized = finalize_execute_job(args, probe)
        result.update(
            passed=True,
            restart_seconds=round(time.time() - restart_started, 2),
            execute_job_id=probe["execute_job_id"],
            dataset_version_id=finalized["job"].get("dataset_version_id"),
            matched_results=finalized["matched_results"],
        )
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result
    finally:
        cleanup_probe(args, probe)


def run_redis_restart_drill(args: argparse.Namespace, compose_args: list[str]) -> dict[str, Any]:
    result = {"name": "redis_restart", "service": args.redis_service, "passed": False}
    probe: dict[str, Any] | None = None
    try:
        probe = prepare_execute_job(args)
        time.sleep(max(args.restart_delay, 0.0))
        restart_started = time.time()
        run_command([*compose_args, "restart", args.redis_service], timeout=300)
        wait_ready(args.base_url, timeout_seconds=300)
        finalized = finalize_execute_job(args, probe)
        result.update(
            passed=True,
            restart_seconds=round(time.time() - restart_started, 2),
            execute_job_id=probe["execute_job_id"],
            dataset_version_id=finalized["job"].get("dataset_version_id"),
            matched_results=finalized["matched_results"],
        )
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result
    finally:
        cleanup_probe(args, probe)


def render_report(base_url: str, results: list[dict[str, Any]]) -> str:
    lines = [
        "# Compose 故障演练记录",
        "",
        f"- 服务地址：`{base_url}`",
        "",
        "| 演练 | 目标服务 | 是否通过 | 关键任务 | 版本号 | 结果行数 | 重启耗时 | 错误 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in results:
        lines.append(
            "| {name} | {service} | {passed} | {job} | {version} | {rows} | {restart} | {error} |".format(
                name=item.get("name", ""),
                service=item.get("service", ""),
                passed="是" if item.get("passed") else "否",
                job=item.get("execute_job_id", ""),
                version=item.get("dataset_version_id", ""),
                rows=item.get("matched_results", ""),
                restart=item.get("restart_seconds", ""),
                error=(item.get("error") or "").replace("\n", " "),
            )
        )
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- 建议在 Compose 环境中设置 `FAULT_INJECTION_JOB_DELAY_SECONDS=5`，让任务在运行态停留更久，便于观察 API / Worker / Redis 重启期间的状态流转。",
            "- 如果没有启用故障演练延迟，任务可能在服务重启前就已经完成，此时脚本仍可作为“任务记录未丢失”的轻量验证，但证据强度会弱一些。",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[failure-drills] failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
