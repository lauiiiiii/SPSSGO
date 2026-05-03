from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import uuid
from typing import Any
from urllib import error, request


ACTIVE_JOB_STATUSES = {"pending", "queued", "running", "retrying"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test the async upload -> analysis -> results flow.")
    parser.add_argument("--base-url", default=os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--username", default=os.environ.get("SMOKE_USERNAME") or os.environ.get("ADMIN_USERNAME", "admin"))
    parser.add_argument("--password", default=os.environ.get("SMOKE_PASSWORD") or os.environ.get("ADMIN_PASSWORD", ""))
    parser.add_argument(
        "--csv-path",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "loadtests", "fixtures", "category_summary_sample.csv"),
    )
    parser.add_argument("--job-timeout", type=int, default=int(os.environ.get("SMOKE_JOB_TIMEOUT", "120")))
    parser.add_argument("--poll-interval", type=float, default=float(os.environ.get("SMOKE_POLL_INTERVAL", "1.0")))
    parser.add_argument("--cleanup-session", action="store_true", default=True)
    parser.add_argument("--keep-session", action="store_true")
    parser.add_argument("--skip-metrics", action="store_true")
    parser.add_argument("--method", default="category_summary")
    parser.add_argument("--group-var", default="group")
    parser.add_argument("--summary-vars", default="score_a,score_b")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.keep_session:
        args.cleanup_session = False
    if not args.password:
        raise SystemExit("Missing --password or ADMIN_PASSWORD/SMOKE_PASSWORD environment variable")
    if not os.path.exists(args.csv_path):
        raise SystemExit(f"Fixture file not found: {args.csv_path}")

    base_url = args.base_url.rstrip("/")
    print(f"[smoke] target={base_url}")
    health = request_json("GET", f"{base_url}/api/health")
    if health["status"] != 200:
        raise RuntimeError(f"health check failed: {health['status']} {health['text']}")
    print("[smoke] /api/health ok")

    ready = request_json("GET", f"{base_url}/api/health/ready")
    if ready["status"] != 200:
        raise RuntimeError(f"readiness check failed: {ready['status']} {ready['text']}")
    print("[smoke] /api/health/ready ok")

    if not args.skip_metrics:
        metrics = request_text("GET", f"{base_url}/metrics")
        if metrics["status"] != 200 or "spssgo_http_requests_total" not in metrics["text"]:
            raise RuntimeError(f"metrics check failed: {metrics['status']}")
        print("[smoke] /metrics ok")

    headers = login_user(base_url, args.username, args.password)
    print(f"[smoke] login ok as {args.username}")

    session_id = create_session(base_url, headers)
    print(f"[smoke] session created: {session_id}")

    try:
        upload_job_id = submit_upload_job(base_url, session_id, args.csv_path, headers)
        print(f"[smoke] upload accepted: job={upload_job_id}")

        upload_job = wait_for_job(base_url, upload_job_id, headers, args.job_timeout, args.poll_interval)
        print(f"[smoke] upload completed: dataset_version_id={upload_job.get('dataset_version_id')}")

        execute_job_id = submit_execute_method_job(
            base_url,
            session_id,
            headers,
            method=args.method,
            group_var=args.group_var,
            summary_vars=[item.strip() for item in args.summary_vars.split(",") if item.strip()],
        )
        print(f"[smoke] execute-method accepted: job={execute_job_id}")

        execute_job = wait_for_job(base_url, execute_job_id, headers, args.job_timeout, args.poll_interval)
        print(f"[smoke] analysis completed: dataset_version_id={execute_job.get('dataset_version_id')}")

        results = fetch_results(base_url, session_id, headers)
        matched = [item for item in results if item.get("job_id") == execute_job_id]
        if not matched:
            raise RuntimeError("no result rows were persisted for the execute-method job")
        print(f"[smoke] results ok: rows={len(matched)}")

        sandbox_runs_resp = request_json(
            "GET",
            f"{base_url}/api/jobs/{execute_job_id}/sandbox-runs",
            headers=headers,
        )
        if sandbox_runs_resp["status"] == 200:
            print(f"[smoke] sandbox runs endpoint ok: count={len(sandbox_runs_resp['json'])}")
        else:
            print(f"[smoke] sandbox runs endpoint returned {sandbox_runs_resp['status']}, continuing")

        print("[smoke] async flow passed")
        return 0
    finally:
        if args.cleanup_session and session_id:
            cleanup_resp = cleanup_session(base_url, session_id, headers)
            if cleanup_resp["status"] == 200:
                print(f"[smoke] session cleaned: {session_id}")
            else:
                print(f"[smoke] cleanup skipped: {cleanup_resp['status']} {cleanup_resp['text']}", file=sys.stderr)


def login_user(base_url: str, username: str, password: str) -> dict[str, str]:
    login = request_json(
        "POST",
        f"{base_url}/api/login",
        json_body={"username": username, "password": password},
    )
    if login["status"] != 200:
        raise RuntimeError(f"login failed: {login['status']} {login['text']}")
    token = login["json"].get("access_token") or login["json"].get("token")
    if not token:
        raise RuntimeError("login response missing access token")
    return {"Authorization": f"Bearer {token}"}


def create_session(base_url: str, headers: dict[str, str]) -> str:
    session_resp = request_json("POST", f"{base_url}/api/session", headers=headers)
    if session_resp["status"] != 200 or not session_resp["json"].get("session_id"):
        raise RuntimeError(f"create session failed: {session_resp['status']} {session_resp['text']}")
    return session_resp["json"]["session_id"]


def submit_upload_job(base_url: str, session_id: str, csv_path: str, headers: dict[str, str]) -> str:
    upload_resp = upload_file(
        f"{base_url}/api/upload/{session_id}",
        csv_path,
        headers=headers,
    )
    upload_payload = parse_json_or_fail(upload_resp)
    upload_job_id = upload_payload.get("job_id")
    if upload_resp["status"] != 200 or not upload_job_id:
        raise RuntimeError(f"upload failed: {upload_resp['status']} {upload_resp['text']}")
    return upload_job_id


def submit_execute_method_job(
    base_url: str,
    session_id: str,
    headers: dict[str, str],
    *,
    method: str,
    group_var: str,
    summary_vars: list[str],
) -> str:
    execute_resp = request_json(
        "POST",
        f"{base_url}/api/execute-method/{session_id}",
        headers={**headers, "Content-Type": "application/json"},
        json_body={
            "method": method,
            "params": {
                "group_var": group_var,
                "summary_vars": summary_vars,
            },
        },
    )
    execute_payload = execute_resp["json"]
    execute_job_id = execute_payload.get("job_id")
    if execute_resp["status"] != 200 or not execute_job_id:
        raise RuntimeError(f"execute-method failed: {execute_resp['status']} {execute_resp['text']}")
    return execute_job_id


def fetch_results(base_url: str, session_id: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    results_resp = request_json("GET", f"{base_url}/api/results/{session_id}", headers=headers)
    if results_resp["status"] != 200:
        raise RuntimeError(f"results failed: {results_resp['status']} {results_resp['text']}")
    return results_resp["json"].get("results") or []


def cleanup_session(base_url: str, session_id: str, headers: dict[str, str]) -> dict[str, Any]:
    return request_json("DELETE", f"{base_url}/api/session/{session_id}", headers=headers)


def wait_for_job(base_url: str, job_id: str, headers: dict[str, str], timeout_seconds: int, poll_interval: float) -> dict[str, Any]:
    started = time.time()
    while time.time() - started < timeout_seconds:
        response = request_json("GET", f"{base_url}/api/jobs/{job_id}", headers=headers)
        if response["status"] != 200:
            raise RuntimeError(f"job status failed for {job_id}: {response['status']} {response['text']}")
        payload = response["json"]
        status = (payload.get("status") or "").lower()
        if status not in ACTIVE_JOB_STATUSES:
            if status != "succeeded":
                raise RuntimeError(f"job {job_id} ended as {status}: {payload.get('error_message') or ''}")
            return payload
        time.sleep(poll_interval)
    raise RuntimeError(f"job {job_id} timed out after {timeout_seconds}s")


def upload_file(url: str, filepath: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    boundary = f"----spssgo-{uuid.uuid4().hex}"
    filename = os.path.basename(filepath)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(filepath, "rb") as handle:
        file_bytes = handle.read()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"),
            f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return request_bytes(
        "POST",
        url,
        body=body,
        headers={
            **(headers or {}),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        timeout=60,
    )


def request_json(method: str, url: str, *, headers: dict[str, str] | None = None, json_body: Any | None = None) -> dict[str, Any]:
    body = None
    extra_headers = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        extra_headers.setdefault("Content-Type", "application/json")
    response = request_bytes(method, url, body=body, headers=extra_headers)
    try:
        payload = json.loads(response["text"]) if response["text"] else {}
    except json.JSONDecodeError:
        payload = {}
    response["json"] = payload
    return response


def request_text(method: str, url: str, *, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return request_bytes(method, url, headers=headers)


def request_bytes(
    method: str,
    url: str,
    *,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    req = request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            return {
                "status": resp.status,
                "headers": dict(resp.headers.items()),
                "content": content,
                "text": content.decode("utf-8", errors="replace"),
            }
    except error.HTTPError as exc:
        content = exc.read()
        return {
            "status": exc.code,
            "headers": dict(exc.headers.items()) if exc.headers else {},
            "content": content,
            "text": content.decode("utf-8", errors="replace"),
        }


def parse_json_or_fail(response: dict[str, Any]) -> dict[str, Any]:
    try:
        return json.loads(response["text"]) if response["text"] else {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"expected JSON response, got: {response['text'][:200]}") from exc


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[smoke] failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
