# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import pandas as pd

from backend.analysis.methods import ahp_professional, ahp_simplified


class AhpMethodsTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "q1": [1, 2, 3, 4],
            "q2": [2, 3, 4, 5],
            "q3": [4, 3, 2, 1],
        })

    def test_simplified_matrix_mode_uses_r(self):
        r_result = {
            "success": True,
            "name": "层次分析法（AHP快速版）",
            "headers": ["准则", "权重", "排序"],
            "rows": [["指标1", "0.5000", "1"], ["指标2", "0.5000", "2"]],
            "description": "AHP 快速版完成",
            "sections": [
                {"type": "table", "title": "一致性检验", "headers": ["指标", "值"], "rows": [["CR", "0.0000"]]},
            ],
        }
        params = {
            "input_mode": "matrix",
            "criteria": ["指标1", "指标2"],
            "matrix": [[1, 1], [1, 1]],
            "weight_method": "sum_product",
        }
        with patch("backend.analysis.methods.ahp_simplified.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.ahp_simplified.run_r_script", return_value=r_result) as run_r:
                result = ahp_simplified.run(self.df, params)

        self.assertEqual(result["name"], "层次分析法（AHP快速版）")
        self.assertEqual(result["rows"][0][1], "0.5000")
        self.assertEqual(run_r.call_args.args[0], "ahp_simplified.R")
        self.assertIsNone(run_r.call_args.kwargs["temp_files"])
        payload = run_r.call_args.kwargs["payload"]
        self.assertEqual(payload["criteria"], ["指标1", "指标2"])
        self.assertEqual(payload["matrix"], [[1, 1], [1, 1]])

    def test_simplified_data_auto_mode_writes_selected_variables(self):
        r_result = {
            "success": True,
            "name": "层次分析法（AHP快速版）",
            "headers": ["准则", "权重", "排序"],
            "rows": [["q1", "0.3333", "1"]],
            "description": "AHP 快速版完成",
        }
        with patch("backend.analysis.methods.ahp_simplified.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.ahp_simplified.run_r_script", return_value=r_result) as run_r:
                result = ahp_simplified.run(
                    self.df,
                    {"input_mode": "data_auto", "variables": ["q1", "q2"], "include_missing_analysis": True},
                )

        self.assertEqual(result["description"], "AHP 快速版完成")
        self.assertEqual(run_r.call_args.args[0], "ahp_simplified.R")
        self.assertIn("ahp_simplified_input.csv", run_r.call_args.kwargs["temp_files"])
        payload = run_r.call_args.kwargs["payload"]
        self.assertEqual(payload["variables"], ["q1", "q2"])
        self.assertTrue(payload["include_missing_analysis"])

    def test_simplified_data_auto_requires_two_variables(self):
        result = ahp_simplified.run(self.df, {"input_mode": "data_auto", "variables": ["q1"]})

        self.assertIn("至少需要 2 个准则变量", result["description"])

    def test_simplified_stale_data_auto_with_matrix_payload_uses_matrix(self):
        r_result = {
            "success": True,
            "name": "层次分析法（AHP快速版）",
            "headers": ["准则", "权重", "排序"],
            "rows": [["指标1", "0.7500", "1"], ["指标2", "0.2500", "2"]],
            "description": "AHP 快速版完成",
        }
        params = {
            "input_mode": "data_auto",
            "variables": [],
            "criteria": ["指标1", "指标2"],
            "matrix": [[1, 3], [1 / 3, 1]],
        }
        with patch("backend.analysis.methods.ahp_simplified.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.ahp_simplified.run_r_script", return_value=r_result) as run_r:
                result = ahp_simplified.run(self.df, params)

        self.assertEqual(result["description"], "AHP 快速版完成")
        payload = run_r.call_args.kwargs["payload"]
        self.assertEqual(payload["input_mode"], "matrix")
        self.assertEqual(payload["criteria"], ["指标1", "指标2"])
        self.assertIsNone(run_r.call_args.kwargs["temp_files"])

    def test_simplified_r_error_is_returned(self):
        with patch("backend.analysis.methods.ahp_simplified.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.ahp_simplified.run_r_script", return_value={"success": False, "error": "判断矩阵必须满足互反关系"}):
                result = ahp_simplified.run(
                    self.df,
                    {"criteria": ["指标1", "指标2"], "matrix": [[1, 3], [1, 1]]},
                )

        self.assertIn("判断矩阵必须满足互反关系", result["description"])

    def test_professional_uses_r_with_three_layer_payload(self):
        r_result = {
            "success": True,
            "name": "层次分析法（AHP专业版）",
            "headers": ["排名", "方案", "综合得分"],
            "rows": [["1", "方案1", "0.7000"], ["2", "方案2", "0.3000"]],
            "description": "AHP 专业版完成",
        }
        params = {
            "goal": "选择最佳方案",
            "criteria": [{"id": "c1", "label": "价格"}, {"id": "c2", "label": "质量"}, {"id": "c3", "label": "服务"}],
            "alternatives": [{"id": "a1", "label": "方案1"}, {"id": "a2", "label": "方案2"}],
            "criteria_matrix": [[1, 3, 5], [1 / 3, 1, 2], [1 / 5, 1 / 2, 1]],
            "alternative_matrices": {
                "c1": [[1, 3], [1 / 3, 1]],
                "c2": [[1, 1 / 5], [5, 1]],
                "c3": [[1, 2], [1 / 2, 1]],
            },
        }
        with patch("backend.analysis.methods.ahp_professional.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.ahp_professional.run_r_script", return_value=r_result) as run_r:
                result = ahp_professional.run(self.df, params)

        self.assertEqual(result["rows"][0], ["1", "方案1", "0.7000"])
        self.assertEqual(run_r.call_args.args[0], "ahp_professional.R")
        payload = run_r.call_args.kwargs["payload"]
        self.assertEqual(payload["goal"], "选择最佳方案")
        self.assertEqual(len(payload["criteria"]), 3)
        self.assertEqual(len(payload["alternatives"]), 2)
        self.assertIn("c1", payload["alternative_matrices"])

    def test_professional_r_failure_is_returned(self):
        with patch("backend.analysis.methods.ahp_professional.is_r_runtime_available", return_value=True):
            with patch("backend.analysis.methods.ahp_professional.run_r_script", side_effect=ahp_professional.RExecutionError("boom")):
                result = ahp_professional.run(self.df, {})

        self.assertIn("R AHP 专业版执行失败", result["description"])


if __name__ == "__main__":
    unittest.main()
