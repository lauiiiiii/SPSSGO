# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.methods import sem


class SemRBridgeTests(unittest.TestCase):
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
            "structural_paths": [{"dependent": "F2", "predictors": ["F1"]}],
        }

    def test_sem_uses_r_when_available(self):
        r_result = {
            "success": True,
            "name": "结构方程模型(SEM)",
            "headers": ["因变量", "自变量"],
            "rows": [["F2", "F1"]],
            "description": "R SEM result",
            "sections": [{"type": "table", "title": "结构路径系数", "headers": [], "rows": []}],
        }
        with patch("backend.analysis.methods.sem.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.sem.run_r_script", return_value=r_result) as run_r:
                result = sem.run(self.df, self.params)

        self.assertEqual(result["description"], "R SEM result")
        self.assertEqual(run_r.call_args.args[0], "sem.R")
        self.assertIn("sem_input.csv", run_r.call_args.kwargs["temp_files"])

    def test_sem_returns_error_when_r_fails(self):
        with patch("backend.analysis.methods.sem.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.sem.run_r_script", side_effect=sem.RExecutionError("boom")):
                result = sem.run(self.df, self.params)

        self.assertEqual(result["name"], "结构方程模型(SEM)")
        self.assertFalse(result["rows"])
        self.assertIn("R 结构方程模型执行失败", result["description"])

    def test_sem_requires_r_runtime(self):
        with patch("backend.analysis.methods.sem.is_r_runtime_available", return_value=False):
            result = sem.run(self.df, self.params)

        self.assertEqual(result["name"], "结构方程模型(SEM)")
        self.assertIn("R 运行环境不可用", result["description"])
