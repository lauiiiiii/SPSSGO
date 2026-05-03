# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.methods import reliability


class ReliabilityRBridgeTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "q1": [1, 2, 3, 4],
                "q2": [1, 2, 3, 4],
                "q3": [2, 3, 4, 5],
            }
        )
        self.params = {"items_groups": {"量表A": ["q1", "q2", "q3"]}}

    def test_reliability_uses_r_when_available(self):
        r_result = {
            "success": True,
            "name": "信度分析",
            "headers": ["Cronbach's α系数"],
            "rows": [["0.900"]],
            "description": "R result",
            "sections": [{"type": "table", "title": "输出结果1：Cronbach's α系数表", "headers": [], "rows": []}],
        }
        with patch("backend.analysis.methods.reliability.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.reliability.run_r_script", return_value=r_result) as run_r:
                result = reliability.reliability_analysis(self.df, self.params)

        self.assertEqual(result["description"], "R result")
        self.assertEqual(run_r.call_args.args[0], "reliability.R")
        self.assertIn("reliability_input.csv", run_r.call_args.kwargs["temp_files"])

    def test_reliability_returns_error_when_r_fails(self):
        with patch("backend.analysis.methods.reliability.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.reliability.run_r_script", side_effect=reliability.RExecutionError("boom")):
                result = reliability.reliability_analysis(self.df, self.params)

        self.assertEqual(result["name"], "信度分析")
        self.assertFalse(result["rows"])
        self.assertIn("R 信度分析执行失败", result["description"])

    def test_reliability_requires_r_runtime(self):
        with patch("backend.analysis.methods.reliability.is_r_runtime_available", return_value=False):
            result = reliability.reliability_analysis(self.df, self.params)

        self.assertEqual(result["name"], "信度分析")
        self.assertIn("R 运行环境不可用", result["description"])
