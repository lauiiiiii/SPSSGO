# -*- coding: utf-8 -*-
import unittest

import pandas as pd

from backend.analysis.methods.choice_multi_single import run as run_multi_single
from backend.analysis.methods.choice_single_multi import run as run_single_multi
from backend.analysis.registry import METHOD_META


class ChoiceMultiSingleAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "group": ["A", "A", "B", "B"],
            "q1": [2, 1, 2, 0],
            "q2": [0, 2, 2, 1],
        })

    def test_multi_single_count_value_supports_non_one_code(self):
        result = run_multi_single(self.df, {
            "single_var": "group",
            "multiple_vars": ["q1", "q2"],
            "count_value": "2",
        })

        self.assertEqual(result["headers"], ["分组题项", "A", "B", "总数", "X²", "P"])
        self.assertEqual(result["rows"][0][:4], ["q1", "1（50%）", "1（50%）", "2"])
        self.assertEqual(result["rows"][1][:4], ["q2", "1（50%）", "1（50%）", "2"])

        titles = [section["title"] for section in result["sections"]]
        self.assertIn("分析步骤", titles)
        self.assertIn("输出结果1：多重响应频率分析表", titles)
        self.assertIn("输出结果2：响应率", titles)
        self.assertIn("输出结果3：普及率", titles)
        self.assertIn("输出结果4：帕累托图分析", titles)
        self.assertIn("输出结果5：多重响应频率交叉分析表", titles)
        self.assertIn("输出结果6：交叉图", titles)
        cross_section = next(section for section in result["sections"] if section["title"] == "输出结果5：多重响应频率交叉分析表")
        self.assertEqual(cross_section["headerRows"][0][1], {"text": "group", "colspan": 2})

    def test_multi_single_frequency_charts_follow_spsspro_modes(self):
        result = run_multi_single(self.df, {
            "single_var": "group",
            "multiple_vars": ["q1", "q2"],
            "count_value": "2",
        })

        response_chart = next(section for section in result["sections"] if section["title"] == "输出结果2：响应率")["charts"][0]
        popularity_chart = next(section for section in result["sections"] if section["title"] == "输出结果3：普及率")["charts"][0]
        cross_chart = next(section for section in result["sections"] if section["title"] == "输出结果6：交叉图")["charts"][0]

        self.assertEqual(response_chart["data"]["defaultMode"], "pie")
        self.assertEqual(popularity_chart["data"]["defaultMode"], "bar")
        self.assertEqual(cross_chart["chartType"], "crosstab_distribution")
        self.assertEqual(cross_chart["data"]["defaultMode"], "column")

    def test_single_multi_count_value_supports_non_one_code(self):
        result = run_single_multi(self.df, {
            "single_var": "group",
            "multiple_vars": ["q1", "q2"],
            "count_value": "2",
        })

        self.assertEqual(result["headers"], ["分组题项", "", "q1", "q2", "总数", "X²", "P"])
        self.assertEqual(result["rows"][0][:5], ["group", "A", "1（50%）", "1（50%）", "2"])
        self.assertEqual(result["rows"][1][:5], ["", "B", "1（50%）", "1（50%）", "2"])
        self.assertEqual(result["rows"][2][:5], ["总计", "", "2", "2", "4"])

        titles = [section["title"] for section in result["sections"]]
        self.assertIn("分析结果", titles)
        self.assertIn("分析步骤", titles)
        self.assertIn("输出结果1：多重响应频率分析表", titles)
        self.assertIn("输出结果5：多重响应频率交叉分析表", titles)
        self.assertIn("输出结果6：交叉图", titles)

    def test_both_methods_expose_count_value_option(self):
        expected_orders = {
            "choice_multi_single": 56,
            "choice_single_multi": 57,
        }
        for method_key, order in expected_orders.items():
            meta = METHOD_META[method_key]
            option = next(item for item in meta["options"] if item["key"] == "count_value")
            self.assertEqual(meta["category"], "问卷分析包")
            self.assertEqual(meta["order"], order)
            self.assertEqual(option["choices"], ["1", "2", "0"])
            self.assertEqual(option["default"], "1")


if __name__ == "__main__":
    unittest.main()
