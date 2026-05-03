# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.methods import factor_analysis


class FactorAnalysisRBridgeTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "q1": [1, 2, 3, 4, 5, 6],
                "q2": [1, 2, 3, 4, 5, 6],
                "q3": [2, 3, 4, 5, 6, 7],
                "q4": [2, 3, 4, 5, 6, 7],
            }
        )
        self.params = {"items": ["q1", "q2", "q3", "q4"], "scale_name": "量表A"}

    def test_factor_analysis_uses_r_when_available(self):
        r_result = {
            "success": True,
            "name": "效度检验：量表A",
            "headers": ["指标", "值"],
            "rows": [["KMO", "0.8000"]],
            "description": "R validity result",
            "sections": [{"type": "table", "title": "KMO和Bartlett检验", "headers": [], "rows": []}],
        }
        with patch("backend.analysis.methods.factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.factor_analysis.run_r_script", return_value=r_result) as run_r:
                result = factor_analysis.factor_analysis_check(self.df, self.params)

        self.assertEqual(result["description"], "R validity result")
        self.assertEqual(run_r.call_args.args[0], "factor_analysis.R")
        self.assertIn("factor_analysis_input.csv", run_r.call_args.kwargs["temp_files"])

    def test_factor_analysis_returns_error_when_r_fails(self):
        with patch("backend.analysis.methods.factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.factor_analysis.run_r_script", side_effect=factor_analysis.RExecutionError("boom")):
                result = factor_analysis.factor_analysis_check(self.df, self.params)

        self.assertEqual(result["name"], "效度检验")
        self.assertFalse(result["rows"])
        self.assertIn("R 效度分析执行失败", result["description"])

    def test_factor_analysis_requires_r_runtime(self):
        with patch("backend.analysis.methods.factor_analysis.is_r_runtime_available", return_value=False):
            result = factor_analysis.factor_analysis_check(self.df, self.params)

        self.assertEqual(result["name"], "效度检验")
        self.assertIn("R 运行环境不可用", result["description"])
