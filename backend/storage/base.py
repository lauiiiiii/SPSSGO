from __future__ import annotations

from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def ensure_session(self, session_id: str) -> None:
        pass

    @abstractmethod
    def save_bytes(self, category: str, session_id: str, relative_path: str, content: bytes) -> None:
        pass

    @abstractmethod
    def save_text(
        self,
        category: str,
        session_id: str,
        relative_path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        pass

    @abstractmethod
    def read_bytes(self, category: str, session_id: str, relative_path: str) -> bytes:
        pass

    @abstractmethod
    def read_text(
        self,
        category: str,
        session_id: str,
        relative_path: str,
        encoding: str = "utf-8",
    ) -> str:
        pass

    @abstractmethod
    def exists(self, category: str, session_id: str, relative_path: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, category: str, session_id: str) -> list[str]:
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        pass

    @abstractmethod
    def materialize_file(self, category: str, session_id: str, relative_path: str) -> str:
        pass

    @abstractmethod
    def release_materialized(self, path: str) -> None:
        pass

    @abstractmethod
    def category_size(self, category: str) -> int:
        pass

    @abstractmethod
    def healthcheck(self) -> dict:
        pass

