# -*- coding: utf-8 -*-
import unittest

import pandas as pd

from backend.analysis.methods.multiple_choice import multiple_choice_analysis


class MultipleChoiceAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "q8_1": [1, 0, 2, None],
            "q8_2": [2, 2, 0, None],
            "q8_3": [0, 2, 2, None],
        })

    def test_count_value_can_use_non_one_code(self):
        result = multiple_choice_analysis(self.df, {
            "variables": ["q8_1", "q8_2", "q8_3"],
            "count_value": "2",
        })

        self.assertEqual(result["headers"], ["多选题选项", "N（计数）", "响应率（%）", "普及率（%）", "X²", "P"])
        self.assertEqual(result["rows"][0][:4], ["q8_1", "1", "20.000", "33.333"])
        self.assertEqual(result["rows"][1][:4], ["q8_2", "2", "40.000", "66.667"])
        self.assertEqual(result["rows"][2][:4], ["q8_3", "2", "40.000", "66.667"])
        self.assertEqual(result["rows"][-1][:4], ["总计", "5", "100.000", "166.667"])

    def test_zero_can_be_selected_as_count_value(self):
        result = multiple_choice_analysis(self.df, {
            "variables": ["q8_1", "q8_2", "q8_3"],
            "count_value": "0",
        })

        self.assertEqual([row[1] for row in result["rows"][:3]], ["1", "1", "1"])
        self.assertEqual(result["rows"][-1][:4], ["总计", "3", "100.000", "100.000"])

    def test_spsspro_style_chart_sections_are_returned(self):
        result = multiple_choice_analysis(self.df, {
            "variables": ["q8_1", "q8_2", "q8_3"],
            "count_value": "2",
        })
        chart_sections = [section for section in result["sections"] if section["type"] == "charts"]

        self.assertEqual([section["title"] for section in chart_sections], ["输出结果2：响应率", "输出结果3：普及率", "输出结果4：帕累托图"])
        self.assertEqual(chart_sections[0]["charts"][0]["chartType"], "category_distribution")
        self.assertEqual(chart_sections[1]["charts"][0]["data"]["percents"], [33.33333333333333, 66.66666666666666, 66.66666666666666])
        self.assertEqual(chart_sections[2]["charts"][0]["chartType"], "metric_comparison")
        self.assertTrue(chart_sections[2]["charts"][0]["data"]["isPareto"])


if __name__ == "__main__":
    unittest.main()
