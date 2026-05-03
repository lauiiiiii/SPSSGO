# -*- coding: utf-8 -*-
import json
import unittest
from unittest.mock import patch

from backend.services.jobs import control as job_control


class JobEventStreamTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_job_events_emits_job_then_done(self):
        queued = {
            "id": "job-1",
            "job_type": "execute_method",
            "status": "queued",
            "queue": "analysis",
            "progress": {"message": "排队中"},
            "result": {},
            "error_message": "",
            "session_id": "sess-1",
            "dataset_id": 1,
            "dataset_version_id": 2,
            "created_at": 1.0,
            "started_at": None,
            "finished_at": None,
        }
        succeeded = {
            **queued,
            "status": "succeeded",
            "progress": {"message": "完成"},
            "result": {"ok": True},
            "finished_at": 2.0,
        }
        jobs = [queued, succeeded]

        async def fake_get_job_detail_for_user(_job_id, _user):
            return jobs.pop(0)

        async def fake_sleep(_seconds):
            return None

        with patch("backend.services.jobs.control.get_job_detail_for_user", side_effect=fake_get_job_detail_for_user):
            with patch("backend.services.jobs.control.asyncio.sleep", side_effect=fake_sleep):
                response = await job_control.stream_job_events("job-1", {"id": 1, "role": "user"})
                chunks = []
                async for chunk in response.body_iterator:
                    chunks.append(chunk)

        payload = "".join(chunks)
        self.assertIn("event: job", payload)
        self.assertIn("event: done", payload)
        statuses = []
        for chunk in chunks:
            lines = [line for line in chunk.splitlines() if line.startswith("data: ")]
            for line in lines:
                data = json.loads(line[6:])
                statuses.append(data["status"])
        self.assertIn("queued", statuses)
        self.assertIn("succeeded", statuses)
