# -*- coding: utf-8 -*-
import unittest
from urllib.parse import quote

from fastapi.middleware.cors import CORSMiddleware

from backend import app_runtime
from backend.app_runtime import download_response
from backend.app import app as api_app


async def _read_streaming_body(response):
    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    return b"".join(chunks)


class DownloadResponseTests(unittest.IsolatedAsyncioTestCase):
    def test_create_app_uses_configured_cors_origins(self):
        original_origins = app_runtime.CORS_ALLOW_ORIGINS
        app_runtime.CORS_ALLOW_ORIGINS = ("https://www.example.com", "https://admin.example.com")
        try:
            app = app_runtime.create_app()
        finally:
            app_runtime.CORS_ALLOW_ORIGINS = original_origins

        cors_middleware = next(
            item for item in app.user_middleware
            if item.cls is CORSMiddleware
        )
        self.assertEqual(
            cors_middleware.kwargs["allow_origins"],
            ["https://www.example.com", "https://admin.example.com"],
        )

    def test_openapi_docs_include_auth_and_route_summary(self):
        schema = api_app.openapi()
        login_doc = schema["paths"]["/api/login"]["post"]
        job_events_doc = schema["paths"]["/api/jobs/{job_id}/events"]["get"]

        self.assertEqual(login_doc["tags"], ["Auth"])
        self.assertEqual(login_doc["summary"], "账号登录")
        self.assertEqual(job_events_doc["tags"], ["Jobs"])
        self.assertIn("SSE", job_events_doc["description"])
        self.assertEqual(job_events_doc["security"], [{"BearerAuth": []}])
        self.assertIn("BearerAuth", schema["components"]["securitySchemes"])
        self.assertEqual(
            login_doc["requestBody"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/LoginRequest",
        )
        self.assertEqual(
            schema["paths"]["/api/jobs/{job_id}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/JobDetail",
        )
        self.assertIn(
            "text/event-stream",
            schema["paths"]["/api/jobs/{job_id}/events"]["get"]["responses"]["200"]["content"],
        )
        self.assertEqual(
            schema["paths"]["/api/jobs/{job_id}/output"]["get"]["responses"]["200"]["content"]["application/octet-stream"]["schema"]["format"],
            "binary",
        )
        self.assertEqual(
            schema["paths"]["/api/jobs/{job_id}"]["get"]["responses"]["429"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/ApiError",
        )
        self.assertEqual(
            schema["paths"]["/api/methods"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/MethodsResponse",
        )
        self.assertEqual(
            schema["paths"]["/api/methods/{method_key}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/MethodDetailResponse",
        )

    def test_download_response_supports_unicode_filename(self):
        filename = "分析结果.docx"

        response = download_response(b"docx-bytes", filename, "application/test-docx")

        disposition = response.headers["content-disposition"]
        self.assertIn('attachment;', disposition)
        self.assertIn('filename="download.docx"', disposition)
        self.assertIn(f"filename*=UTF-8''{quote(filename, safe='!#$&+-.^_`|~')}", disposition)
        self.assertEqual(response.media_type, "application/test-docx")

    def test_download_response_keeps_ascii_filename(self):
        filename = "report.docx"

        response = download_response(b"docx-bytes", filename, "application/test-docx")

        disposition = response.headers["content-disposition"]
        self.assertIn('filename="report.docx"', disposition)
        self.assertIn("filename*=UTF-8''report.docx", disposition)

    async def test_download_response_streams_original_content(self):
        content = b"\x50\x4b\x03\x04docx"

        response = download_response(content, "分析结果.docx", "application/test-docx")
        streamed = await _read_streaming_body(response)

        self.assertEqual(streamed, content)
