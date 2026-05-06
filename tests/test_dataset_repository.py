# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import backend.database  # noqa: F401
from backend.repositories import dataset_repository


class _FakeCursor:
    def __init__(self, *, rows=None, one=None):
        self.rows = rows or []
        self.one = one
        self.executed = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, sql, params=None):
        self.executed.append((sql, params))

    async def fetchall(self):
        return self.rows

    async def fetchone(self):
        return self.one


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


class DatasetRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_list_dataset_versions_includes_source_job_payload(self):
        cursor = _FakeCursor(rows=[
            {
                "id": 11,
                "dataset_id": 7,
                "owner_id": 1,
                "session_id": "sess-1",
                "version_no": 3,
                "source_job_id": "job-1",
                "storage_key": "v3.parquet",
                "status": "ready",
                "summary_json": '{"total_rows": 10}',
                "preview_json": "[]",
                "schema_json": "[]",
                "created_at": 1.0,
                "source_job_status": "succeeded",
                "source_job_type": "process_data",
                "source_job_payload_json": '{"method": "standardize"}',
            }
        ])

        with patch.object(dataset_repository.db, "_pool", _FakePool(_FakeConnection(cursor))):
            versions = await dataset_repository.list_dataset_versions(7)

        self.assertIn("LEFT JOIN jobs", cursor.executed[0][0])
        self.assertEqual(versions[0]["source_method"], "standardize")
        self.assertEqual(versions[0]["source_job_status"], "succeeded")
        self.assertEqual(versions[0]["source_job_type"], "process_data")
        self.assertEqual(versions[0]["summary"], {"total_rows": 10})

    async def test_count_datasets_for_owner_uses_search_filter(self):
        cursor = _FakeCursor(one=(5,))

        with patch.object(dataset_repository.db, "_pool", _FakePool(_FakeConnection(cursor))):
            total = await dataset_repository.count_datasets_for_owner(1, query="满意度")

        sql, params = cursor.executed[0]
        self.assertIn("d.owner_id = %s", sql)
        self.assertIn("d.name LIKE %s", sql)
        self.assertEqual(params[0], 1)
        self.assertEqual(params[1:], ["%满意度%", "%满意度%", "%满意度%", "%满意度%"])
        self.assertEqual(total, 5)
