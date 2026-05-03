# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from backend.services.jobs import common as job_common


class JobFaultInjectionTests(unittest.IsolatedAsyncioTestCase):
    def test_should_apply_fault_injection_delay_is_disabled_by_default(self):
        with patch.object(job_common, "FAULT_INJECTION_JOB_DELAY_SECONDS", 0.0):
            with patch.object(job_common, "FAULT_INJECTION_JOB_DELAY_TYPES", ()):
                self.assertFalse(job_common.should_apply_fault_injection_delay("execute_method"))

    def test_should_apply_fault_injection_delay_can_target_specific_job_types(self):
        with patch.object(job_common, "FAULT_INJECTION_JOB_DELAY_SECONDS", 3.0):
            with patch.object(job_common, "FAULT_INJECTION_JOB_DELAY_TYPES", ("execute_method", "ai_plan")):
                self.assertTrue(job_common.should_apply_fault_injection_delay("execute_method"))
                self.assertFalse(job_common.should_apply_fault_injection_delay("upload_ingest"))

    async def test_maybe_fault_injection_delay_updates_progress_and_sleeps(self):
        job = {"id": "job-1", "job_type": "execute_method"}

        with patch.object(job_common, "FAULT_INJECTION_JOB_DELAY_SECONDS", 2.5):
            with patch.object(job_common, "FAULT_INJECTION_JOB_DELAY_TYPES", ("all",)):
                with patch("backend.services.jobs.common.update_job", new=AsyncMock()) as update_job:
                    with patch("backend.services.jobs.common.asyncio.sleep", new=AsyncMock()) as sleep:
                        await job_common.maybe_fault_injection_delay(job)

        update_job.assert_awaited_once()
        sleep.assert_awaited_once_with(2.5)
