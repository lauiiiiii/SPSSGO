# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

import pandas as pd

from backend.services.jobs import runner


class _Materialized:
    def __call__(self, _session_id, _storage_key):
        return self

    def __enter__(self):
        return "C:\\fake\\v1.parquet"

    def __exit__(self, exc_type, exc, tb):
        return False


class _AsyncLock:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class ExecuteMethodJobScoreWritebackTests(unittest.IsolatedAsyncioTestCase):
    async def test_efa_score_columns_create_and_activate_new_dataset_version(self):
        df = pd.DataFrame(
            {
                "q1": [1, 2, 3],
                "q2": [2, 3, 4],
                "FactorScore_1": [9.0, 9.0, 9.0],
            }
        )
        job = {
            "id": "job-1",
            "session_id": "sess-1",
            "owner_id": 7,
            "dataset_version_id": 5,
            "payload": {"method": "exploratory_factor_analysis", "params": {"variables": ["q1", "q2"]}},
        }
        current_version = {"id": 5, "version_no": 1, "storage_key": "v1.parquet"}
        next_version = {"id": 9, "version_no": 2, "storage_key": "v2.parquet"}
        method_result = {
            "name": "因子分析（探索性）",
            "headers": ["指标", "值"],
            "rows": [["KMO值", "0.812"]],
            "description": "ok",
            "sections": [],
            "score_columns": [
                {"base_name": "FactorScore_1", "values": [0.11, None, 0.33]},
                {"base_name": "CompScore_1", "values": [0.21, None, 0.43]},
            ],
        }

        async def passthrough_to_thread(func, *args, **kwargs):
            return func(*args, **kwargs)

        with patch("backend.services.jobs.runner.get_dataset_version", new=AsyncMock(return_value=current_version)):
            with patch("backend.services.jobs.runner.get_current_dataset_version_for_session", new=AsyncMock(return_value=current_version)):
                with patch("backend.services.jobs.runner.parse_data_file_async", new=AsyncMock(return_value=(df, {}))):
                    with patch("backend.services.jobs.runner.inject_analysis_metadata", new=AsyncMock(return_value=job["payload"]["params"])):
                        with patch("backend.services.jobs.runner.append_optional_missing_analysis", return_value=method_result):
                            with patch("backend.services.jobs.runner.asyncio.to_thread", new=passthrough_to_thread):
                                with patch.dict(runner.METHOD_REGISTRY, {"exploratory_factor_analysis": lambda _df, _params: method_result}, clear=False):
                                    with patch("backend.services.jobs.runner._materialized_dataset", new=_Materialized()):
                                        with patch("backend.services.jobs.runner.session_write_lock", return_value=_AsyncLock()):
                                            with patch("backend.services.jobs.runner.create_dataset_version_from_dataframe", new=AsyncMock(return_value=(next_version, {"row_count": 3}))) as create_version:
                                                with patch("backend.services.jobs.runner.save_current_metadata_snapshot", new=AsyncMock()) as save_snapshot:
                                                    with patch("backend.services.jobs.runner.activate_dataset_version", new=AsyncMock(return_value=next_version)) as activate_version:
                                                        with patch("backend.services.jobs.runner.delete_results_for_job", new=AsyncMock()):
                                                            with patch("backend.services.jobs.runner.save_result", new=AsyncMock()) as save_result:
                                                                with patch("backend.services.jobs.runner.update_session", new=AsyncMock()):
                                                                    result = await runner._run_execute_method_job(job)

        self.assertTrue(result["created_dataset_version"])
        self.assertEqual(result["dataset_version_id"], 9)
        self.assertEqual(result["dataset_version_no"], 2)
        self.assertEqual(result["created_columns"], ["FactorScore_1_2", "CompScore_1"])
        create_version.assert_awaited_once()
        created_df = create_version.await_args.args[2]
        self.assertIn("FactorScore_1_2", created_df.columns)
        self.assertIn("CompScore_1", created_df.columns)
        self.assertTrue(pd.isna(created_df["FactorScore_1_2"].tolist()[1]))
        save_snapshot.assert_awaited_once_with("sess-1", "v2.parquet")
        activate_version.assert_awaited_once_with("sess-1", 9)
        self.assertEqual(save_result.await_args_list[0].kwargs["dataset_version_id"], 9)

    async def test_efa_without_saved_scores_does_not_create_dataset_version(self):
        df = pd.DataFrame({"q1": [1, 2, 3], "q2": [2, 3, 4]})
        job = {
            "id": "job-2",
            "session_id": "sess-2",
            "owner_id": 8,
            "dataset_version_id": 6,
            "payload": {"method": "exploratory_factor_analysis", "params": {"variables": ["q1", "q2"]}},
        }
        current_version = {"id": 6, "version_no": 1, "storage_key": "v1.parquet"}
        method_result = {
            "name": "因子分析（探索性）",
            "headers": [],
            "rows": [],
            "description": "ok",
            "sections": [],
        }

        async def passthrough_to_thread(func, *args, **kwargs):
            return func(*args, **kwargs)

        with patch("backend.services.jobs.runner.get_dataset_version", new=AsyncMock(return_value=current_version)):
            with patch("backend.services.jobs.runner.get_current_dataset_version_for_session", new=AsyncMock(return_value=current_version)):
                with patch("backend.services.jobs.runner.parse_data_file_async", new=AsyncMock(return_value=(df, {}))):
                    with patch("backend.services.jobs.runner.inject_analysis_metadata", new=AsyncMock(return_value=job["payload"]["params"])):
                        with patch("backend.services.jobs.runner.append_optional_missing_analysis", return_value=method_result):
                            with patch("backend.services.jobs.runner.asyncio.to_thread", new=passthrough_to_thread):
                                with patch.dict(runner.METHOD_REGISTRY, {"exploratory_factor_analysis": lambda _df, _params: method_result}, clear=False):
                                    with patch("backend.services.jobs.runner._materialized_dataset", new=_Materialized()):
                                        with patch("backend.services.jobs.runner.create_dataset_version_from_dataframe", new=AsyncMock()) as create_version:
                                            with patch("backend.services.jobs.runner.delete_results_for_job", new=AsyncMock()):
                                                with patch("backend.services.jobs.runner.save_result", new=AsyncMock()) as save_result:
                                                    with patch("backend.services.jobs.runner.update_session", new=AsyncMock()):
                                                        result = await runner._run_execute_method_job(job)

        self.assertFalse(result["created_dataset_version"])
        self.assertEqual(result["dataset_version_id"], 6)
        self.assertEqual(result["created_columns"], [])
        create_version.assert_not_awaited()
        self.assertEqual(save_result.await_args_list[0].kwargs["dataset_version_id"], 6)

    async def test_dea_score_columns_create_and_activate_new_dataset_version(self):
        df = pd.DataFrame({"x1": [1, 2, 3], "y1": [1, 2, 3]})
        job = {
            "id": "job-3",
            "session_id": "sess-3",
            "owner_id": 9,
            "dataset_version_id": 7,
            "payload": {"method": "data_envelopment_analysis", "params": {"input_vars": ["x1"], "output_vars": ["y1"], "save_efficiency": True}},
        }
        current_version = {"id": 7, "version_no": 1, "storage_key": "v1.parquet"}
        next_version = {"id": 10, "version_no": 2, "storage_key": "v2.parquet"}
        method_result = {
            "name": "数据包络分析",
            "headers": ["决策单元", "综合效益"],
            "rows": [["1", "1.000"]],
            "description": "ok",
            "sections": [],
            "score_columns": [
                {"base_name": "DEA_综合效益", "values": [1.0, 0.8, 1.0]},
            ],
        }

        async def passthrough_to_thread(func, *args, **kwargs):
            return func(*args, **kwargs)

        with patch("backend.services.jobs.runner.get_dataset_version", new=AsyncMock(return_value=current_version)):
            with patch("backend.services.jobs.runner.get_current_dataset_version_for_session", new=AsyncMock(return_value=current_version)):
                with patch("backend.services.jobs.runner.parse_data_file_async", new=AsyncMock(return_value=(df, {}))):
                    with patch("backend.services.jobs.runner.inject_analysis_metadata", new=AsyncMock(return_value=job["payload"]["params"])):
                        with patch("backend.services.jobs.runner.append_optional_missing_analysis", return_value=method_result):
                            with patch("backend.services.jobs.runner.asyncio.to_thread", new=passthrough_to_thread):
                                with patch.dict(runner.METHOD_REGISTRY, {"data_envelopment_analysis": lambda _df, _params: method_result}, clear=False):
                                    with patch("backend.services.jobs.runner._materialized_dataset", new=_Materialized()):
                                        with patch("backend.services.jobs.runner.session_write_lock", return_value=_AsyncLock()):
                                            with patch("backend.services.jobs.runner.create_dataset_version_from_dataframe", new=AsyncMock(return_value=(next_version, {"row_count": 3}))) as create_version:
                                                with patch("backend.services.jobs.runner.save_current_metadata_snapshot", new=AsyncMock()):
                                                    with patch("backend.services.jobs.runner.activate_dataset_version", new=AsyncMock(return_value=next_version)):
                                                        with patch("backend.services.jobs.runner.delete_results_for_job", new=AsyncMock()):
                                                            with patch("backend.services.jobs.runner.save_result", new=AsyncMock()) as save_result:
                                                                with patch("backend.services.jobs.runner.update_session", new=AsyncMock()):
                                                                    result = await runner._run_execute_method_job(job)

        self.assertTrue(result["created_dataset_version"])
        self.assertEqual(result["created_columns"], ["DEA_综合效益"])
        created_df = create_version.await_args.args[2]
        self.assertIn("DEA_综合效益", created_df.columns)
        self.assertEqual(created_df["DEA_综合效益"].tolist(), [1.0, 0.8, 1.0])
        self.assertEqual(save_result.await_args_list[0].kwargs["dataset_version_id"], 10)
