# Local backend dev runner with a simple file watcher.
# This keeps hot restart off uvicorn's Windows reloader, which can flood stderr.
"""Run the backend and restart it when Python files under backend/ change."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
WATCH_DIR = ROOT_DIR / "backend"
POLL_SECONDS = 1.0
UVICORN_CMD = [
    sys.executable,
    "-m",
    "uvicorn",
    "backend.app:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
]


def snapshot_backend_files() -> dict[Path, int]:
    """Return mtimes for backend Python files that should trigger restart."""
    snapshot: dict[Path, int] = {}
    for path in WATCH_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            snapshot[path] = path.stat().st_mtime_ns
        except OSError:
            continue
    return snapshot


def stop_process(process: subprocess.Popen[bytes]) -> None:
    """Stop the uvicorn child without leaving the port occupied."""
    if process.poll() is not None:
        return
    if os.name == "nt":
        process.terminate()
    else:
        process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def start_process() -> subprocess.Popen[bytes]:
    """Start plain uvicorn; hot restart is handled by this script."""
    print("[backend-dev] starting backend on http://localhost:8000", flush=True)
    return subprocess.Popen(UVICORN_CMD, cwd=ROOT_DIR)


def main() -> int:
    """Watch backend files and restart the child server after code changes."""
    previous = snapshot_backend_files()
    process = start_process()
    try:
        while True:
            time.sleep(POLL_SECONDS)
            if process.poll() is not None:
                return process.returncode or 0
            current = snapshot_backend_files()
            if current != previous:
                print("[backend-dev] backend file changed; restarting", flush=True)
                stop_process(process)
                process = start_process()
                previous = current
    except KeyboardInterrupt:
        print("[backend-dev] stopping", flush=True)
        stop_process(process)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
