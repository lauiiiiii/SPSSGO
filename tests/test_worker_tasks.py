# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from backend import worker_tasks


class WorkerTaskFailureSyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_worker_job_with_failure_sync_passes_successful_jobs(self):
        with patch("backend.worker_tasks._run_worker_job", new=AsyncMock()) as run_worker_job:
            with patch("backend.worker_tasks._mark_job_failed", new=AsyncMock()) as mark_failed:
                await worker_tasks._run_worker_job_with_failure_sync("job-1")

        run_worker_job.assert_awaited_once_with("job-1")
        mark_failed.assert_not_awaited()

    async def test_run_worker_job_with_failure_sync_marks_job_failed_on_error(self):
        exc = RuntimeError("boom")

        with patch("backend.worker_tasks._run_worker_job", new=AsyncMock(side_effect=exc)) as run_worker_job:
            with patch("backend.worker_tasks._mark_job_failed", new=AsyncMock()) as mark_failed:
                with self.assertRaises(RuntimeError):
                    await worker_tasks._run_worker_job_with_failure_sync("job-2")

        run_worker_job.assert_awaited_once_with("job-2")
        mark_failed.assert_awaited_once_with("job-2", exc)
