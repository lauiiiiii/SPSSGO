# -*- coding: utf-8 -*-
import unittest

import pandas as pd

from backend.analysis.common import inject_cross_metadata
from backend.analysis.methods.cross_tabulation import (
    METHOD_META,
    cross_tabulation_analysis,
)


class CrossTabulationAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "q1_1": [1, 1, 2, 2, 2, None],
                "q1_2": [1, 2, 1, 2, 2, 1],
                "q1_3": ["A", "A", "B", "B", "A", "B"],
            }
        )

    def test_meta_matches_spsspro_style_slots(self):
        slots = METHOD_META["slots"]

        self.assertEqual(slots[0]["key"], "group_var")
        self.assertEqual(slots[0]["prefixLabel"], "分组")
        self.assertEqual(slots[0]["type"], "single")
        self.assertEqual(slots[0]["accept"], "any")
        self.assertEqual(slots[1]["key"], "variables")
        self.assertEqual(slots[1]["type"], "multiple")
        self.assertEqual(slots[1]["accept"], "any")
        self.assertEqual(METHOD_META["options"][0]["key"], "percent_base")
        self.assertEqual(METHOD_META["options"][0]["default"], "百分数(按列)")

    def test_multiple_x_variables_are_supported(self):
        result = cross_tabulation_analysis(
            self.df,
            {"group_var": "q1_1", "variables": ["q1_2", "q1_3"]},
        )

        titles = [section["title"] for section in result["sections"]]
        self.assertIn("输出结果1：列联表", titles)
        self.assertIn("输出结果2：交叉图", titles)
        self.assertIn("χ²", result["headers"])
        self.assertIn("p", result["headers"])
        self.assertIn("q1_1 × q1_2", result["description"])
        self.assertIn("q1_1 × q1_3", result["description"])
        chart_section = next(section for section in result["sections"] if section["type"] == "charts")
        self.assertEqual(len(chart_section["charts"]), 2)
        self.assertEqual(chart_section["charts"][0]["chartType"], "crosstab_distribution")

    def test_table_display_modes_match_spssau_switch(self):
        result = cross_tabulation_analysis(
            self.df,
            {"group_var": "q1_1", "variables": ["q1_2"]},
        )

        table = next(section for section in result["sections"] if section["type"] == "table")
        modes = {mode["key"]: mode for mode in table["displayModes"]}

        self.assertEqual(table["displayModeTitle"], "交叉(卡方)分析结果")
        self.assertEqual(table["defaultDisplayMode"], "count_percent")
        self.assertEqual(modes["count_percent"]["label"], "数字(占比)")
        self.assertEqual(modes["count"]["label"], "数字")
        self.assertEqual(modes["percent"]["label"], "百分比")
        self.assertIn("(", modes["count_percent"]["rows"][0][2])
        self.assertNotIn("(", modes["count"]["rows"][0][2])
        self.assertTrue(modes["percent"]["rows"][0][2].endswith("%"))

    def test_percent_base_can_switch_to_row_percent(self):
        result = cross_tabulation_analysis(
            self.df,
            {
                "group_var": "q1_1",
                "variables": ["q1_2"],
                "percent_base": "百分数(按行)",
            },
        )

        table = next(section for section in result["sections"] if section["type"] == "table")
        modes = {mode["key"]: mode for mode in table["displayModes"]}
        self.assertEqual(modes["count_percent"]["rows"][1][2], "1(33.33)")
        self.assertEqual(modes["percent"]["rows"][1][2], "33.33%")
        self.assertIn("行百分比", table["description"])

        chart_section = next(section for section in result["sections"] if section["type"] == "charts")
        self.assertEqual(chart_section["charts"][0]["data"]["percentBase"], "row")

    def test_legacy_var1_var2_params_still_work(self):
        result = cross_tabulation_analysis(
            self.df,
            {"var1": "q1_1", "var2": "q1_2"},
        )

        self.assertEqual(result["headers"][0], "题目")
        self.assertTrue(result["rows"])

    def test_same_group_and_x_variable_is_filtered(self):
        result = cross_tabulation_analysis(
            self.df,
            {"group_var": "q1_1", "variables": ["q1_1", "q1_2"]},
        )

        self.assertIn("q1_1 × q1_2", result["description"])
        self.assertNotIn("q1_1 × q1_1", result["description"])

    def test_cross_metadata_supports_new_and_legacy_params(self):
        params = inject_cross_metadata(
            {"group_var": "q1_1", "variables": ["q1_2"]},
            {
                "q1_1": {"value_labels": {1: "男", 2: "女"}},
                "q1_2": {"value_labels": {1: "低", 2: "高"}},
            },
        )

        self.assertEqual(params["group_labels"]["1"], "男")
        self.assertEqual(params["labels_by_variable"]["q1_2"]["2"], "高")


if __name__ == "__main__":
    unittest.main()
