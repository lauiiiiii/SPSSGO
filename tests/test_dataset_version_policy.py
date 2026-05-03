# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

import pandas as pd
from fastapi import HTTPException

from backend.services import session_data_service, upload_service


class DatasetVersionPolicyTests(unittest.IsolatedAsyncioTestCase):
    async def test_preview_rejects_legacy_upload_for_regular_runtime(self):
        with patch("backend.services.session_data_service.get_current_dataset_version_for_session", new=AsyncMock(return_value=None)):
            with patch("backend.services.session_data_service.find_data_file_name", return_value="legacy.csv"):
                with self.assertRaises(HTTPException) as ctx:
                    await session_data_service.resolve_session_data_source(
                        "sess-1",
                        allow_legacy_fallback=False,
                    )

        self.assertEqual(ctx.exception.status_code, 409)
        self.assertIn("旧上传兼容路径", str(ctx.exception.detail))

    async def test_preview_allows_legacy_upload_for_compat_mode(self):
        frame = pd.DataFrame({"group": ["A", "B"], "score": [1, 2]})
        source = {
            "session_id": "sess-1",
            "storage_category": "uploads",
            "storage_key": "legacy.csv",
            "filename": "legacy.csv",
            "dataset_version_id": None,
            "dataset_version_no": None,
            "source": "legacy_upload",
        }

        with patch("backend.services.upload_service.get_session", new=AsyncMock(return_value={"id": "sess-1"})):
            with patch("backend.services.upload_service.resolve_session_data_source", new=AsyncMock(return_value=source)):
                with patch("backend.services.upload_service.storage_service.materialize_file", return_value="C:\\fake\\legacy.csv"):
                    with patch("backend.services.upload_service.storage_service.release_materialized"):
                        with patch("backend.services.upload_service.parse_data_file", return_value=(frame, {})):
                            payload = await upload_service.build_data_preview_for_session(
                                "sess-1",
                                allow_legacy_fallback=True,
                            )

        self.assertEqual(payload["source"], "legacy_upload")
        self.assertEqual(payload["filename"], "legacy.csv")
        self.assertEqual(payload["total_rows"], 2)

    async def test_download_prefers_dataset_version_over_legacy_upload(self):
        source = {
            "session_id": "sess-1",
            "storage_category": "datasets",
            "storage_key": "abc.parquet",
            "filename": "abc.parquet",
            "dataset_version_id": 8,
            "dataset_version_no": 3,
            "source": "dataset_version",
        }

        with patch("backend.services.upload_service.get_session", new=AsyncMock(return_value={"id": "sess-1"})):
            with patch("backend.services.upload_service.resolve_session_data_source", new=AsyncMock(return_value=source)):
                with patch("backend.services.upload_service.storage_service.read_bytes", return_value=b"parquet-bytes") as read_bytes:
                    with patch("backend.services.upload_service.download_response", return_value={"ok": True}) as response_builder:
                        payload = await upload_service.download_data_file_for_session("sess-1")

        self.assertEqual(payload, {"ok": True})
        read_bytes.assert_called_once_with("datasets", "sess-1", "abc.parquet")
        response_builder.assert_called_once()

    async def test_processing_legacy_upload_requires_compat_permission(self):
        with patch("backend.services.session_data_service.get_current_dataset_version_for_session", new=AsyncMock(return_value=None)):
            with patch("backend.services.session_data_service.find_data_file_name", return_value="legacy.csv"):
                with self.assertRaises(HTTPException) as ctx:
                    await session_data_service.resolve_session_data_source(
                        "sess-1",
                        allow_legacy_fallback=False,
                    )

        self.assertEqual(ctx.exception.status_code, 409)
        self.assertIn("旧上传兼容路径", str(ctx.exception.detail))

    async def test_processing_legacy_upload_still_works_in_compat_mode(self):
        frame = pd.DataFrame({"x": [1]})
        source = {
            "session_id": "sess-1",
            "storage_category": "uploads",
            "storage_key": "legacy.csv",
            "filename": "legacy.csv",
            "dataset_version_id": None,
            "dataset_version_no": None,
            "source": "legacy_upload",
        }

        with patch("backend.services.session_data_service.resolve_session_data_source", new=AsyncMock(return_value=source)):
            with patch("backend.services.session_data_service.storage_service.materialize_file", return_value="C:\\fake\\legacy.csv"):
                with patch("backend.services.session_data_service.storage_service.release_materialized"):
                    with patch("backend.services.session_data_service.load_dataframe", return_value=frame):
                        result = await session_data_service.load_session_dataframe(
                            "sess-1",
                            allow_legacy_fallback=True,
                        )

        self.assertEqual(list(result.columns), ["x"])
