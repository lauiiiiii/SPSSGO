# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, Mock, patch

from backend.services.jobs import common as job_common


class JobDispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_dispatch_job_records_celery_task_without_rewriting_status(self):
        job = {"id": "job-1", "queue": "analysis"}
        task = type("CeleryTaskResult", (), {"id": "celery-1"})()
        execute_job_task = Mock()
        execute_job_task.apply_async.return_value = task

        with patch.object(job_common, "JOB_BACKEND", "celery"):
            with patch("backend.services.jobs.common.update_job", new=AsyncMock()) as update_job:
                with patch("backend.worker_tasks.execute_job_task", new=execute_job_task):
                    await job_common.dispatch_job(job)

        execute_job_task.apply_async.assert_called_once_with(args=["job-1"], queue="analysis")
        update_job.assert_awaited_once_with("job-1", celery_task_id="celery-1")
