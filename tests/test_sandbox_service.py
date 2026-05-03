# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from backend.services import sandbox_service


class SandboxServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_finish_sandbox_audit_updates_status_and_details(self):
        execution = {
            "execution_id": "exec-1",
            "details": {"backend": "local"},
            "executor_mode": None,
            "docker_image": None,
            "container_name": None,
            "started_at": 10.0,
        }
        result = {
            "success": True,
            "audit": {
                "executor_mode": "docker",
                "docker_image": "img",
                "container_name": "ctr",
                "exit_code": 0,
            },
        }

        with patch("backend.services.sandbox_service.time.time", return_value=12.5):
            with patch("backend.services.sandbox_service.update_sandbox_execution", new=AsyncMock()) as update_exec:
                with patch("backend.services.sandbox_service.record_sandbox_execution") as record_exec:
                    await sandbox_service.finish_sandbox_audit(execution, result)

        update_exec.assert_awaited_once()
        _, kwargs = update_exec.await_args
        self.assertEqual(kwargs["status"], "succeeded")
        self.assertEqual(kwargs["executor_mode"], "docker")
        self.assertEqual(kwargs["exit_code"], 0)
        self.assertEqual(kwargs["details"]["backend"], "local")
        self.assertEqual(kwargs["details"]["docker_image"], "img")
        record_exec.assert_called_once()
