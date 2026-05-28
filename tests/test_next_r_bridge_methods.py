# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.methods import (
    discrimination,
    intraclass_correlation,
    mediation,
    moderation,
    multiple_regression,
    parallel_mediation,
    path_analysis,
    serial_mediation,
)


class NextRBridgeMethodsTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "m": [2, 2, 4, 4, 6, 6, 8, 8, 10, 10],
                "m2": [1, 3, 3, 5, 5, 7, 7, 9, 9, 11],
                "w": [5, 4, 6, 5, 7, 6, 8, 7, 9, 8],
                "y": [3, 4, 5, 7, 8, 9, 10, 12, 13, 14],
                "group": ["A", "B", "A", "B", "A", "C", "C", "B", "A", "C"],
                "r1": [1, 2, 3, 4, 5, 5, 4, 3, 2, 1],
                "r2": [1, 2, 3, 4, 5, 5, 4, 3, 2, 1],
            }
        )
        self.cases = [
            {
                "module": path_analysis,
                "call": path_analysis.run,
                "params": {"dependent": "y", "predictors": ["x", "m"]},
                "script": "path_analysis.R",
                "temp_file": "path_analysis_input.csv",
                "failure_text": "R 路径分析执行失败",
                "unavailable_text": "路径分析需要 R 引擎执行",
            },
            {
                "module": mediation,
                "call": mediation.mediation_analysis,
                "params": {"x": "x", "m": "m", "y": "y"},
                "script": "mediation.R",
                "temp_file": "mediation_input.csv",
                "failure_text": "R 中介效应分析执行失败",
                "unavailable_text": "中介效应分析需要 R 引擎执行",
            },
            {
                "module": parallel_mediation,
                "call": parallel_mediation.run,
                "params": {"x": "x", "mediators": ["m", "m2"], "y": "y"},
                "script": "parallel_mediation.R",
                "temp_file": "parallel_mediation_input.csv",
                "failure_text": "R 平行中介效应执行失败",
                "unavailable_text": "平行中介效应需要 R 引擎执行",
            },
            {
                "module": serial_mediation,
                "call": serial_mediation.run,
                "params": {"x": "x", "mediators": ["m", "m2"], "y": "y"},
                "script": "serial_mediation.R",
                "temp_file": "serial_mediation_input.csv",
                "failure_text": "R 链式中介效应执行失败",
                "unavailable_text": "链式中介效应需要 R 引擎执行",
            },
            {
                "module": moderation,
                "call": moderation.moderation_analysis,
                "params": {"x": "x", "w": "w", "y": "y", "controls": ["r1"], "data_process": "标准化"},
                "script": "moderation.R",
                "temp_file": "moderation_input.csv",
                "failure_text": "R 调节效应分析执行失败",
                "unavailable_text": "调节效应分析需要 R 引擎执行",
            },
            {
                "module": multiple_regression,
                "call": multiple_regression.multiple_regression,
                "params": {
                    "dependent": "y",
                    "predictors": ["x", "group"],
                    "include_missing_analysis": True,
                    "variable_meta": {
                        "x": {"display_name": "X值", "var_type": "numeric", "value_labels": {}},
                        "y": {"display_name": "Y值", "var_type": "numeric", "value_labels": {}},
                        "group": {
                            "display_name": "分组",
                            "var_type": "categorical",
                            "value_labels": {"A": "A组", "B": "B组", "C": "C组"},
                        },
                    },
                },
                "script": "multiple_regression.R",
                "temp_file": "multiple_regression_input.csv",
                "failure_text": "R 线性回归执行失败",
                "unavailable_text": "线性回归需要 R 引擎执行",
            },
            {
                "module": intraclass_correlation,
                "call": intraclass_correlation.run,
                "params": {"variables": ["r1", "r2"]},
                "script": "intraclass_correlation.R",
                "temp_file": "intraclass_correlation_input.csv",
                "failure_text": "R 组内相关系数执行失败",
                "unavailable_text": "组内相关系数需要 R 引擎执行",
            },
            {
                "module": discrimination,
                "call": discrimination.run,
                "params": {"variables": ["x", "m", "m2"]},
                "script": "discrimination.R",
                "temp_file": "discrimination_input.csv",
                "failure_text": "R 区分度分析执行失败",
                "unavailable_text": "区分度分析需要 R 引擎执行",
            },
        ]

    def test_methods_use_r_when_available(self):
        r_result = {
            "success": True,
            "name": "R result",
            "headers": ["指标"],
            "rows": [["1"]],
            "description": "R bridge result",
            "sections": [{"type": "table", "title": "R 输出", "headers": [], "rows": []}],
        }
        for case in self.cases:
            with self.subTest(script=case["script"]):
                module_name = case["module"].__name__
                with patch(f"{module_name}.is_r_runtime_available", return_value=True):
                    with patch(f"{module_name}.run_r_script", return_value=r_result) as run_r:
                        result = case["call"](self.df, case["params"])

                self.assertEqual(result["description"], "R bridge result")
                self.assertEqual(run_r.call_args.args[0], case["script"])
                self.assertIn(case["temp_file"], run_r.call_args.kwargs["temp_files"])
                if case["script"] == "moderation.R":
                    payload = run_r.call_args.kwargs["payload"]
                    self.assertEqual(payload["controls"], ["r1"])
                    self.assertEqual(payload["data_process"], "标准化")
                if case["script"] == "multiple_regression.R":
                    payload = run_r.call_args.kwargs["payload"]
                    self.assertEqual(payload["dependent"], "y")
                    self.assertEqual(payload["predictors"], ["x", "group"])
                    self.assertTrue(payload["include_missing_analysis"])
                    self.assertEqual(payload["variable_meta"]["group"]["display_name"], "分组")
                    self.assertEqual(payload["variable_meta"]["group"]["var_type"], "categorical")
                    self.assertEqual(
                        run_r.call_args.kwargs["temp_files"]["multiple_regression_input.csv"].splitlines()[0],
                        "y,x,group",
                    )

    def test_methods_return_error_when_r_fails(self):
        for case in self.cases:
            with self.subTest(script=case["script"]):
                module_name = case["module"].__name__
                with patch(f"{module_name}.is_r_runtime_available", return_value=True):
                    with patch(f"{module_name}.run_r_script", side_effect=case["module"].RExecutionError("boom")):
                        result = case["call"](self.df, case["params"])

                self.assertFalse(result["rows"])
                self.assertIn(case["failure_text"], result["description"])

    def test_methods_require_r_runtime(self):
        for case in self.cases:
            with self.subTest(script=case["script"]):
                module_name = case["module"].__name__
                with patch(f"{module_name}.is_r_runtime_available", return_value=False):
                    result = case["call"](self.df, case["params"])

                self.assertFalse(result["rows"])
                self.assertIn(case["unavailable_text"], result["description"])


if __name__ == "__main__":
    unittest.main()
