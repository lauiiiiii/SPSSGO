# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from backend.services import analysis_service, shared_report_service


class SharedReportServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_snapshot_invalidates_old_links_for_same_results(self):
        body = {
            "session_id": "sess-1",
            "report_title": "描述统计",
            "report_meta_tags": ["V1"],
            "result_ids": [11, "11", 12, "bad"],
            "display_results": [{"name": "描述统计", "sections": []}],
            "ai_result": "",
            "expiry_days": 7,
            "password": "abcd",
        }
        user = {"id": 9}

        with patch("backend.services.shared_report_service.get_session_or_404", new=AsyncMock(return_value={"id": "sess-1"})):
            with patch(
                "backend.services.shared_report_service.create_shared_report",
                new=AsyncMock(return_value={"share_token": "new-token", "created_at": 1.0, "expires_at": 2.0}),
            ) as create_shared_report:
                with patch(
                    "backend.services.shared_report_service.delete_shared_reports_for_exact_result_ids",
                    new=AsyncMock(return_value=1),
                ) as delete_old_links:
                    result = await shared_report_service.create_shared_report_snapshot(body, user)

        payload = create_shared_report.await_args.args[2]
        self.assertEqual(payload["result_ids"], [11, 12])
        delete_old_links.assert_awaited_once_with(
            "sess-1",
            [11, 12],
            report_title="描述统计",
            exclude_share_token="new-token",
        )
        self.assertEqual(result["share_token"], "new-token")

    async def test_delete_analysis_result_invalidates_related_share_links(self):
        with patch("backend.services.analysis_service.get_session", new=AsyncMock(return_value={"id": "sess-2"})):
            with patch(
                "backend.services.analysis_service.get_results",
                new=AsyncMock(return_value=[{"id": 21, "analysis_name": "交叉分析"}]),
            ):
                with patch("backend.services.analysis_service.delete_result", new=AsyncMock(return_value=True)) as delete_result:
                    with patch(
                        "backend.services.analysis_service.delete_shared_reports_for_overlapping_result_ids",
                        new=AsyncMock(return_value=2),
                    ) as delete_links:
                        result = await analysis_service.delete_analysis_result_for_session("sess-2", 21)

        delete_result.assert_awaited_once_with("sess-2", 21)
        delete_links.assert_awaited_once_with("sess-2", [21], report_title="交叉分析")
        self.assertEqual(result, {"success": True, "id": 21})
