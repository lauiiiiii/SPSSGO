# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.registry import build_execute_params
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
        self.assertEqual(run_r.call_args.kwargs["payload"]["items_groups"], {"量表A": ["q1", "q2", "q3"]})

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

    def test_legacy_variables_are_built_as_single_dimension(self):
        params = build_execute_params("reliability", {
            "variables": ["q1", "q2", "q3"],
            "type": "Cronbach's α",
        })

        self.assertEqual(params["items_groups"], {"分析变量": ["q1", "q2", "q3"]})
        self.assertEqual(params["type"], "Cronbach's α")

    def test_dimension_slots_are_built_as_named_groups(self):
        params = build_execute_params("reliability", {
            "dimension1_vars": ["q1", "q2"],
            "dimension2_vars": ["q3", "q4"],
            "dimension3_vars": [],
            "dimension_labels": {
                "dimension1_vars": "学习兴趣",
                "dimension2_vars": "学习动机",
            },
            "type": "Cronbach's α",
        })

        self.assertEqual(params["items_groups"], {
            "学习兴趣": ["q1", "q2"],
            "学习动机": ["q3", "q4"],
        })

    def test_dimension_payload_keeps_renamed_groups(self):
        df = pd.DataFrame({
            "q1": [1, 2, 3],
            "q2": [1, 2, 3],
            "q3": [2, 3, 4],
            "q4": [2, 3, 4],
        })
        params = {
            "items_groups": {
                "学习兴趣": ["q1", "q2"],
                "学习动机": ["q3", "q4"],
            },
            "type": "Cronbach's α",
        }

        payload, csv_text = reliability._build_r_payload(df, params["items_groups"], params["type"])

        self.assertEqual(payload["items_groups"], params["items_groups"])
        self.assertIn("q1,q2,q3,q4", csv_text)
