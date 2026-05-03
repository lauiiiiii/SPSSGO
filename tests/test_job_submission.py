# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from backend.services.jobs import submission as job_submission


class JobSubmissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_enqueue_job_uses_queue_template_and_dispatches(self):
        created_job = {"id": "job-1", "status": "queued", "queue": "analysis", "job_type": "execute_method"}

        with patch("backend.services.jobs.submission.create_job", new=AsyncMock(return_value=created_job)) as create_job:
            with patch("backend.services.jobs.submission.record_enqueued_job") as record_enqueued_job:
                with patch("backend.services.jobs.submission.update_job", new=AsyncMock()) as update_job:
                    with patch("backend.services.jobs.submission.dispatch_job", new=AsyncMock()) as dispatch_job:
                        job = await job_submission._enqueue_job(
                            "execute_method",
                            7,
                            session_id="sess-1",
                            dataset_id=3,
                            dataset_version_id=5,
                            payload={"method": "demo"},
                            progress_message="分析任务已入队",
                        )

        self.assertEqual(job, created_job)
        create_job.assert_awaited_once_with(
            "execute_method",
            7,
            "analysis",
            session_id="sess-1",
            dataset_id=3,
            dataset_version_id=5,
            payload={"method": "demo"},
            status="queued",
        )
        record_enqueued_job.assert_called_once_with(created_job)
        update_job.assert_awaited_once_with("job-1", progress={"stage": "queued", "message": "分析任务已入队"})
        dispatch_job.assert_awaited_once_with(created_job)
