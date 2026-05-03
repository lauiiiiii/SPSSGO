# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.methods import confirmatory_factor_analysis


class ConfirmatoryFactorAnalysisRBridgeTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "q1": [1, 2, 3, 4, 5, 6],
                "q2": [1, 2, 3, 4, 5, 6],
                "q3": [2, 3, 4, 5, 6, 7],
                "q4": [3, 4, 5, 6, 7, 8],
            }
        )
        self.params = {
            "factor1_vars": ["q1", "q2"],
            "factor2_vars": ["q3", "q4"],
        }

    def test_cfa_uses_r_when_available(self):
        r_result = {
            "success": True,
            "name": "验证性因子分析",
            "headers": ["因子", "题项"],
            "rows": [["F1", "q1"]],
            "description": "R CFA result",
            "sections": [{"type": "table", "title": "输出结果2：因子载荷系数表", "headers": [], "rows": []}],
        }
        with patch("backend.analysis.methods.confirmatory_factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.confirmatory_factor_analysis.run_r_script", return_value=r_result) as run_r:
                result = confirmatory_factor_analysis.confirmatory_factor_analysis(self.df, self.params)

        self.assertEqual(result["description"], "R CFA result")
        self.assertEqual(run_r.call_args.args[0], "confirmatory_factor_analysis.R")
        self.assertIn("cfa_input.csv", run_r.call_args.kwargs["temp_files"])

    def test_cfa_returns_error_when_r_fails(self):
        with patch("backend.analysis.methods.confirmatory_factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.confirmatory_factor_analysis.run_r_script", side_effect=confirmatory_factor_analysis.RExecutionError("boom")):
                result = confirmatory_factor_analysis.confirmatory_factor_analysis(self.df, self.params)

        self.assertEqual(result["name"], "验证性因子分析")
        self.assertFalse(result["rows"])
        self.assertIn("R 验证性因子分析执行失败", result["description"])

    def test_cfa_requires_r_runtime(self):
        with patch("backend.analysis.methods.confirmatory_factor_analysis.is_r_runtime_available", return_value=False):
            result = confirmatory_factor_analysis.confirmatory_factor_analysis(self.df, self.params)

        self.assertEqual(result["name"], "验证性因子分析")
        self.assertIn("R 运行环境不可用", result["description"])
