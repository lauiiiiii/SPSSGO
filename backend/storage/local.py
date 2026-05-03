from __future__ import annotations

import os
import shutil
import uuid

from .base import BaseStorage


class LocalStorage(BaseStorage):
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.temp_dir = os.path.join(self.root_dir, ".cache")

    def initialize(self) -> None:
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        for category in ("uploads", "outputs", "datasets"):
            os.makedirs(os.path.join(self.root_dir, category), exist_ok=True)

    def ensure_session(self, session_id: str) -> None:
        for category in ("uploads", "outputs", "datasets"):
            os.makedirs(self._session_dir(category, session_id), exist_ok=True)

    def save_bytes(self, category: str, session_id: str, relative_path: str, content: bytes) -> None:
        filepath = self._path(category, session_id, relative_path)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(content)

    def save_text(
        self,
        category: str,
        session_id: str,
        relative_path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        filepath = self._path(category, session_id, relative_path)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding=encoding) as f:
            f.write(content)

    def read_bytes(self, category: str, session_id: str, relative_path: str) -> bytes:
        with open(self._path(category, session_id, relative_path), "rb") as f:
            return f.read()

    def read_text(
        self,
        category: str,
        session_id: str,
        relative_path: str,
        encoding: str = "utf-8",
    ) -> str:
        with open(self._path(category, session_id, relative_path), "r", encoding=encoding) as f:
            return f.read()

    def exists(self, category: str, session_id: str, relative_path: str) -> bool:
        return os.path.exists(self._path(category, session_id, relative_path))

    def list_files(self, category: str, session_id: str) -> list[str]:
        session_dir = self._session_dir(category, session_id)
        if not os.path.isdir(session_dir):
            return []
        names = []
        for entry in os.scandir(session_dir):
            if entry.is_file():
                names.append(entry.name)
        names.sort()
        return names

    def delete_session(self, session_id: str) -> None:
        for category in ("uploads", "outputs", "datasets"):
            shutil.rmtree(self._session_dir(category, session_id), ignore_errors=True)

    def materialize_file(self, category: str, session_id: str, relative_path: str) -> str:
        return self._path(category, session_id, relative_path)

    def release_materialized(self, path: str) -> None:
        return None

    def category_size(self, category: str) -> int:
        category_dir = os.path.join(self.root_dir, category)
        total = 0
        if os.path.isdir(category_dir):
            for dirpath, _, filenames in os.walk(category_dir):
                for name in filenames:
                    filepath = os.path.join(dirpath, name)
                    if os.path.isfile(filepath):
                        total += os.path.getsize(filepath)
        return total

    def healthcheck(self) -> dict:
        try:
            self.initialize()
            marker = os.path.join(self.root_dir, f".healthcheck-{uuid.uuid4().hex}.tmp")
            with open(marker, "w", encoding="utf-8") as handle:
                handle.write("ok")
            os.remove(marker)
            return {
                "ok": True,
                "backend": "local",
                "root_dir": self.root_dir,
                "writable": True,
            }
        except Exception as exc:
            return {
                "ok": False,
                "backend": "local",
                "root_dir": self.root_dir,
                "detail": str(exc),
            }

    def _session_dir(self, category: str, session_id: str) -> str:
        return os.path.join(self.root_dir, category, session_id)

    def _path(self, category: str, session_id: str, relative_path: str) -> str:
        normalized = relative_path.replace("/", os.sep)
        return os.path.join(self._session_dir(category, session_id), normalized)

