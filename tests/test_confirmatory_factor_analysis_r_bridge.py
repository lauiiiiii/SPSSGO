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
        option_keys = [option["key"] for option in confirmatory_factor_analysis.METHOD_META["options"]]
        self.assertIn("second_order_model", option_keys)

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
        self.assertEqual(
            run_r.call_args.kwargs["payload"]["factor_map"],
            {"因子1": ["q1", "q2"], "因子2": ["q3", "q4"]},
        )
        self.assertFalse(run_r.call_args.kwargs["payload"]["second_order_model"])

    def test_cfa_can_request_second_order_model(self):
        r_result = {
            "success": True,
            "name": "验证性因子分析",
            "headers": [],
            "rows": [],
            "description": "second order",
            "sections": [],
        }
        params = {**self.params, "second_order_model": True}
        with patch("backend.analysis.methods.confirmatory_factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.confirmatory_factor_analysis.run_r_script", return_value=r_result) as run_r:
                result = confirmatory_factor_analysis.confirmatory_factor_analysis(self.df, params)

        self.assertEqual(result["description"], "second order")
        self.assertTrue(run_r.call_args.kwargs["payload"]["second_order_model"])
        self.assertEqual(run_r.call_args.kwargs["payload"]["second_order_factor"], "二阶模型1")
        self.assertEqual(run_r.call_args.kwargs["payload"]["second_order_members"], ["因子1", "因子2"])
        self.assertEqual(
            run_r.call_args.kwargs["payload"]["second_order_models"],
            [{"name": "二阶模型1", "members": ["因子1", "因子2"]}],
        )

    def test_cfa_respects_selected_second_order_members(self):
        r_result = {
            "success": True,
            "name": "验证性因子分析",
            "headers": [],
            "rows": [],
            "description": "selected second order",
            "sections": [],
        }
        df = self.df.assign(q5=[2, 3, 4, 5, 6, 7], q6=[3, 4, 5, 6, 7, 8])
        params = {
            **self.params,
            "factor3_vars": ["q5", "q6"],
            "second_order_model": True,
            "second_order_members": ["factor1_vars", "factor3_vars"],
        }
        with patch("backend.analysis.methods.confirmatory_factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.confirmatory_factor_analysis.run_r_script", return_value=r_result) as run_r:
                result = confirmatory_factor_analysis.confirmatory_factor_analysis(df, params)

        self.assertEqual(result["description"], "selected second order")
        self.assertEqual(run_r.call_args.kwargs["payload"]["second_order_members"], ["因子1", "因子3"])

    def test_cfa_supports_multiple_second_order_models(self):
        r_result = {
            "success": True,
            "name": "验证性因子分析",
            "headers": [],
            "rows": [],
            "description": "multi second order",
            "sections": [],
        }
        df = self.df.assign(q5=[2, 3, 4, 5, 6, 7], q6=[3, 4, 5, 6, 7, 8], q7=[3, 4, 5, 6, 7, 8], q8=[4, 5, 6, 7, 8, 9])
        params = {
            **self.params,
            "factor3_vars": ["q5", "q6"],
            "factor4_vars": ["q7", "q8"],
            "second_order_model": True,
            "second_order_models": [
                {"name": "体验质量", "members": ["factor1_vars", "factor2_vars"]},
                {"name": "服务质量", "members": ["factor3_vars", "factor4_vars"]},
            ],
        }
        with patch("backend.analysis.methods.confirmatory_factor_analysis.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.confirmatory_factor_analysis.run_r_script", return_value=r_result) as run_r:
                result = confirmatory_factor_analysis.confirmatory_factor_analysis(df, params)

        self.assertEqual(result["description"], "multi second order")
        self.assertEqual(
            run_r.call_args.kwargs["payload"]["second_order_models"],
            [
                {"name": "体验质量", "members": ["因子1", "因子2"]},
                {"name": "服务质量", "members": ["因子3", "因子4"]},
            ],
        )

    def test_second_order_requires_at_least_two_first_order_factors(self):
        params = {"factor1_vars": ["q1", "q2", "q3"], "second_order_model": True}

        result = confirmatory_factor_analysis.confirmatory_factor_analysis(self.df, params)

        self.assertIn("二阶因子模型至少需要2个一阶因子", result["description"])

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
