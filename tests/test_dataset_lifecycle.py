# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import backend.database  # noqa: F401
import backend.repositories.session_repository as session_repository


class _FakeCursor:
    def __init__(self):
        self.executed = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, sql, params=None):
        self.executed.append((sql, params))


class _FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def cursor(self, *args, **kwargs):
        return self._cursor


class _FakeAcquire:
    def __init__(self, connection):
        self._connection = connection

    async def __aenter__(self):
        return self._connection

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakePool:
    def __init__(self, connection):
        self._connection = connection

    def acquire(self):
        return _FakeAcquire(self._connection)


class DatasetLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_delete_session_removes_storage_after_db_record(self):
        cursor = _FakeCursor()
        pool = _FakePool(_FakeConnection(cursor))

        with patch.object(session_repository.db, "_pool", pool):
            with patch.object(session_repository.storage_service, "delete_session") as delete_storage:
                await session_repository.delete_session("sess-1")

        self.assertEqual(cursor.executed, [("DELETE FROM sessions WHERE id = %s", ("sess-1",))])
        delete_storage.assert_called_once_with("sess-1")

    async def test_delete_session_does_not_fail_when_storage_cleanup_fails(self):
        cursor = _FakeCursor()
        pool = _FakePool(_FakeConnection(cursor))

        with patch.object(session_repository.db, "_pool", pool):
            with patch.object(session_repository.storage_service, "delete_session", side_effect=RuntimeError("disk busy")):
                with patch.object(session_repository.logger, "exception") as log_exception:
                    await session_repository.delete_session("sess-2")

        self.assertEqual(cursor.executed, [("DELETE FROM sessions WHERE id = %s", ("sess-2",))])
        log_exception.assert_called_once()
