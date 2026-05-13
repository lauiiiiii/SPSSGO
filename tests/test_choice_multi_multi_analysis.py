# -*- coding: utf-8 -*-
import unittest

import pandas as pd

from backend.analysis.methods.choice_multi_multi import run
from backend.analysis.registry import METHOD_META


class ChoiceMultiMultiAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "q8_1": [1, 1, 0, 0],
            "q8_2": [0, 1, 1, 0],
            "q16_1": [1, 0, 1, 0],
            "q16_2": [0, 1, 1, 0],
        })

    def test_returns_spsspro_style_sections(self):
        result = run(self.df, {
            "variables_a": ["q8_1", "q8_2"],
            "variables_b": ["q16_1", "q16_2"],
        })

        self.assertEqual(result["name"], "多选-多选（交叉分析）")
        self.assertEqual(result["headers"], ["分组题项", "q16_1", "q16_2", "总数", "X²", "P"])
        self.assertEqual(result["rows"][0][:4], ["q8_1", "1（50.000%）", "1（50.000%）", "2"])
        self.assertEqual(result["rows"][1][:4], ["q8_2", "1（33.333%）", "2（66.667%）", "3"])
        self.assertEqual(result["rows"][-1][:4], ["总计", "2", "3", "5"])

        titles = [section["title"] for section in result["sections"]]
        self.assertIn("输出结果1：多重响应频率分析表", titles)
        self.assertIn("输出结果5：多重响应频率分析表", titles)
        self.assertIn("输出结果9：多重响应频率交叉分析表", titles)
        self.assertIn("输出结果10：交叉图", titles)

    def test_method_meta_is_in_questionnaire_package(self):
        meta = METHOD_META["choice_multi_multi"]

        self.assertEqual(meta["label"], "多选-多选（交叉分析）")
        self.assertEqual(meta["category"], "问卷分析包")
        self.assertEqual(meta["order"], 55)
        self.assertEqual(meta["slots"][0]["label"], "二分类0-1变量")

    def test_count_value_supports_non_one_code(self):
        df = pd.DataFrame({
            "a1": [2, 0, 2],
            "a2": [0, 2, 2],
            "b1": [2, 2, 0],
            "b2": [0, 2, 2],
        })

        result = run(df, {
            "variables_a": ["a1", "a2"],
            "variables_b": ["b1", "b2"],
            "count_value": "2",
        })

        self.assertEqual(result["rows"][0][:4], ["a1", "1（50.000%）", "1（50.000%）", "2"])
        self.assertEqual(result["rows"][1][:4], ["a2", "1（33.333%）", "2（66.667%）", "3"])

    def test_cross_chart_uses_common_crosstab_protocol(self):
        result = run(self.df, {
            "variables_a": ["q8_1", "q8_2"],
            "variables_b": ["q16_1", "q16_2"],
        })
        chart_section = next(section for section in result["sections"] if section["title"] == "输出结果10：交叉图")
        chart = chart_section["charts"][0]

        self.assertEqual(chart["chartType"], "crosstab_distribution")
        self.assertEqual(chart["data"]["groupLabels"], ["q16_1", "q16_2"])
        self.assertEqual(chart["data"]["xLabels"], ["q8_1", "q8_2"])
        self.assertEqual(chart["data"]["matrix"], [[1, 1], [1, 2]])
        self.assertEqual(chart["data"]["defaultMode"], "column")
        self.assertEqual(chart["data"]["defaultLabelMode"], "count")


if __name__ == "__main__":
    unittest.main()
