# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

import pandas as pd

from backend.services.jobs import aux_runner


class JobAuxRunnerTests(unittest.TestCase):
    def test_build_interpretation_prompt_includes_table_and_text_sections(self):
        payload = {
            "method": "相关分析",
            "sections": [
                {"type": "table", "title": "结果表", "headers": ["A", "B"], "rows": [[1, 2]], "note": "note"},
                {"type": "advice", "title": "建议", "content": "more"},
            ],
        }

        method_name, messages = aux_runner.build_interpretation_prompt(payload)

        self.assertEqual(method_name, "相关分析")
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("结果表", messages[1]["content"])
        self.assertIn("建议", messages[1]["content"])

    def test_run_process_data_job_returns_new_version_payload(self):
        job = {"id": "job-1", "session_id": "sess-1", "owner_id": 7, "payload": {"method": "dummy", "params": {"x": 1}}}
        version = {"storage_key": "v1.parquet"}
        dataset = {"id": 3}
        next_df = pd.DataFrame({"x": [1, 2]})

        class _Materialized:
            def __call__(self, _session_id, _storage_key):
                return self

            def __enter__(self):
                return "C:\\fake\\v1.parquet"

            def __exit__(self, exc_type, exc, tb):
                return False

        async def _run():
            with patch("backend.services.jobs.aux_runner.parse_data_file_async", new=AsyncMock(return_value=(pd.DataFrame({"x": [1]}), {}))):
                with patch("backend.services.jobs.aux_runner.asyncio.to_thread", new=AsyncMock(return_value=(next_df, "done"))):
                    with patch("backend.services.jobs.aux_runner.create_dataset_version_from_dataframe", new=AsyncMock(return_value=({"id": 9, "version_no": 2, "storage_key": "v2.parquet"}, {"row_count": 2}))):
                        with patch("backend.services.jobs.aux_runner.persist_processing_metadata", new=AsyncMock()) as persist_metadata:
                            with patch("backend.services.jobs.aux_runner.save_current_metadata_snapshot", new=AsyncMock()) as save_snapshot:
                                with patch("backend.services.jobs.aux_runner.update_session", new=AsyncMock()) as update_session:
                                    return await aux_runner.run_process_data_job(job, version, dataset, _Materialized())

        result = __import__("asyncio").run(_run())
        self.assertEqual(result["dataset_version_id"], 9)
        self.assertEqual(result["dataset_version_no"], 2)
        self.assertEqual(result["message"], "done")
