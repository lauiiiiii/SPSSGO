# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.methods import exploratory_factor_analysis


class ExploratoryFactorAnalysisRBridgeTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "q1": [1, 2, 3, 4, 5, 6],
                "q2": [1, 2, 3, 4, 5, 6],
                "q3": [2, 3, 4, 5, 6, 7],
                "q4": [2, 3, 4, 5, 6, 7],
            }
        )
        self.params = {
            "variables": ["q1", "q2", "q3", "q4"],
            "factor_count": 2,
            "rotation_method": "promax",
            "output_correlation_matrix": True,
            "save_factor_scores": True,
            "save_composite_score": True,
        }

    def test_efa_uses_r_when_available(self):
        r_result = {
            "success": True,
            "name": "因子分析（探索性）",
            "headers": ["指标", "值"],
            "rows": [["KMO", "0.8000"]],
            "description": "R EFA result",
            "sections": [{"type": "table", "title": "KMO和Bartlett检验", "headers": [], "rows": []}],
        }
        with patch("backend.analysis.methods.exploratory_factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.exploratory_factor_analysis.run_r_script", return_value=r_result) as run_r:
                result = exploratory_factor_analysis.run(self.df, self.params)

        self.assertEqual(result["description"], "R EFA result")
        self.assertEqual(run_r.call_args.args[0], "exploratory_factor_analysis.R")
        self.assertIn("efa_input.csv", run_r.call_args.kwargs["temp_files"])
        payload = run_r.call_args.kwargs["payload"]
        self.assertEqual(payload["factor_count"], 2)
        self.assertEqual(payload["rotation_method"], "promax")
        self.assertTrue(payload["output_correlation_matrix"])
        self.assertTrue(payload["save_factor_scores"])
        self.assertTrue(payload["save_composite_score"])
        self.assertEqual(payload["row_id_column"], "__row_id__")
        self.assertIn("__row_id__", run_r.call_args.kwargs["temp_files"]["efa_input.csv"])

    def test_efa_returns_error_when_r_fails(self):
        with patch("backend.analysis.methods.exploratory_factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.exploratory_factor_analysis.run_r_script", side_effect=exploratory_factor_analysis.RExecutionError("boom")):
                result = exploratory_factor_analysis.run(self.df, self.params)

        self.assertEqual(result["name"], "因子分析（探索性）")
        self.assertFalse(result["rows"])
        self.assertIn("R 探索性因子分析执行失败", result["description"])

    def test_efa_requires_r_runtime(self):
        with patch("backend.analysis.methods.exploratory_factor_analysis.is_r_runtime_available", return_value=False):
            result = exploratory_factor_analysis.run(self.df, self.params)

        self.assertEqual(result["name"], "因子分析（探索性）")
        self.assertIn("R 运行环境不可用", result["description"])
