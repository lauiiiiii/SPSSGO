# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from backend.services import upload_ingest_service


class UploadIngestServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_ingest_uploaded_file_updates_questionnaire_text(self):
        fake_file = type("Upload", (), {"filename": "survey.docx", "read": AsyncMock(return_value=b"doc-bytes")})()
        session = {"questionnaire_text": "old"}

        with patch("backend.services.upload_ingest_service.storage_service.save_bytes"):
            with patch("backend.services.upload_ingest_service.storage_service.materialize_file", return_value="C:\\fake\\survey.docx"):
                with patch("backend.services.upload_ingest_service.storage_service.release_materialized"):
                    with patch("backend.services.upload_ingest_service.parse_questionnaire", return_value="new questionnaire"):
                        with patch("backend.services.upload_ingest_service.storage_service.save_text"):
                            with patch("backend.services.upload_ingest_service.update_session", new=AsyncMock()) as update_session:
                                result = await upload_ingest_service.ingest_uploaded_file("sess-1", session, fake_file)

        self.assertEqual(result["filename"], "survey.docx")
        self.assertEqual(result["questionnaire_preview"], "new questionnaire"[:500])
        update_session.assert_awaited_once()
        _, kwargs = update_session.await_args
        self.assertIn("new questionnaire", kwargs["questionnaire_text"])

    def test_validate_upload_file_rejects_large_payload(self):
        with self.assertRaises(HTTPException) as ctx:
            upload_ingest_service.validate_upload_file("demo.csv", 1024 * 1024 * 1024)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("限制", str(ctx.exception.detail))
