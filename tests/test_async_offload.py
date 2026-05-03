# -*- coding: utf-8 -*-
import unittest
from unittest.mock import ANY, AsyncMock, call, patch

import pandas as pd

from backend.services import auth_service, dataset_version_service


class AsyncOffloadTests(unittest.IsolatedAsyncioTestCase):
    async def test_authenticate_user_offloads_password_verification(self):
        user = {"id": 7, "is_active": 1, "password_hash": "hashed-value"}
        run_auth_blocking = AsyncMock(return_value=True)

        with patch("backend.services.auth_service.get_user_by_username", new=AsyncMock(return_value=dict(user))):
            with patch("backend.services.auth_service.touch_user_last_login", new=AsyncMock()) as touch_login:
                with patch("backend.services.auth_service._run_auth_blocking", new=run_auth_blocking):
                    result = await auth_service.authenticate_user("demo", "secret")

        self.assertTrue(result)
        run_auth_blocking.assert_awaited_once_with(auth_service.verify_password, "secret", "hashed-value")
        touch_login.assert_awaited_once_with(7)

    async def test_change_password_offloads_hashing(self):
        run_auth_blocking = AsyncMock(return_value="hashed-password")

        with patch("backend.services.auth_service.update_user", new=AsyncMock()) as update_user:
            with patch("backend.services.auth_service.revoke_user_refresh_tokens", new=AsyncMock()) as revoke_tokens:
                with patch("backend.services.auth_service._run_auth_blocking", new=run_auth_blocking):
                    await auth_service.change_password(9, "new-secret")

        run_auth_blocking.assert_awaited_once_with(auth_service.hash_password, "new-secret")
        update_user.assert_awaited_once_with(9, password_hash="hashed-password")
        revoke_tokens.assert_awaited_once_with(9)

    async def test_create_dataset_version_offloads_parquet_artifact_work(self):
        frame = pd.DataFrame({"score": [1, 2, 3]})
        summary = {"preview_rows": [], "columns": [], "total_rows": 3}
        version = {"id": 11, "version_no": 2}
        to_thread = AsyncMock(side_effect=[(b"parquet-bytes", summary), None])

        with patch("backend.services.dataset_version_service.get_dataset_for_session", new=AsyncMock(return_value={"id": 3})):
            with patch("backend.services.dataset_version_service.create_dataset_version", new=AsyncMock(return_value=version)) as create_version:
                with patch("backend.services.dataset_version_service.asyncio.to_thread", new=to_thread):
                    created_version, created_summary = await dataset_version_service.create_dataset_version_from_dataframe(
                        "sess-1",
                        5,
                        frame,
                        source_job_id="job-1",
                    )

        self.assertEqual(created_version, version)
        self.assertEqual(created_summary, summary)
        to_thread.assert_has_awaits(
            [
                call(dataset_version_service._build_dataset_version_artifacts, frame),
                call(dataset_version_service.storage_service.save_bytes, "datasets", "sess-1", ANY, b"parquet-bytes"),
            ]
        )
        create_version.assert_awaited_once()
