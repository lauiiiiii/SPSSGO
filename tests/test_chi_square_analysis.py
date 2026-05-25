# -*- coding: utf-8 -*-
import unittest

import pandas as pd

from backend.analysis.methods.chi_square import METHOD_META, chi_square_test


class ChiSquareAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "q1": [1] * 60 + [2] * 35,
                "q2": [1] * 9 + [2] * 19 + [3] * 15 + [4] * 12 + [5] * 4 + [6] * 1
                + [1] * 2 + [2] * 8 + [3] * 9 + [4] * 7 + [5] * 4 + [6] * 5,
                "q3": [1] * 21 + [2] * 36 + [3] * 3 + [1] * 4 + [2] * 22 + [3] * 9,
            }
        )

    def test_meta_matches_spsspro_style_slots(self):
        slots = METHOD_META["slots"]

        self.assertEqual(slots[0]["key"], "var1")
        self.assertEqual(slots[0]["prefixLabel"], "分组")
        self.assertEqual(slots[0]["type"], "single")
        self.assertEqual(slots[1]["key"], "variables")
        self.assertEqual(slots[1]["type"], "multiple")
        self.assertEqual(METHOD_META["options"][0]["key"], "test_type")
        self.assertEqual(METHOD_META["options"][0]["default"], "Pearson卡方检验")

    def test_multiple_y_variables_outputs_table_heatmap_and_effects(self):
        result = chi_square_test(self.df, {"var1": "q1", "variables": ["q2", "q3"]})

        titles = [section["title"] for section in result["sections"]]
        self.assertIn("输出结果1：卡方检验分析结果", titles)
        self.assertIn("输出结果2：卡方交叉热力图", titles)
        self.assertIn("输出结果3：效应量化分析", titles)
        self.assertIn("q1 × q2、q3", result["name"])

        table = next(section for section in result["sections"] if section["title"] == "输出结果1：卡方检验分析结果")
        self.assertEqual(table["headerRows"][0][2]["text"], "q1")
        self.assertEqual(table["rows"][0][0]["text"], "q2")
        self.assertEqual(table["rows"][0][-3]["text"], "pearson卡方检验")
        self.assertEqual(table["rows"][0][-2]["text"], "8.423")
        self.assertEqual(table["rows"][0][-1]["text"], "0.134")
        self.assertEqual(table["rows"][7][0]["text"], "q3")
        self.assertEqual(table["rows"][7][-2]["text"], "12.206")
        self.assertEqual(table["rows"][7][-1]["text"], "0.002***")

        chart_section = next(section for section in result["sections"] if section["type"] == "charts")
        self.assertEqual(len(chart_section["charts"]), 2)
        self.assertEqual(chart_section["charts"][0]["chartType"], "crosstab_distribution")
        self.assertEqual(chart_section["charts"][0]["data"]["defaultMode"], "heatmap")
        self.assertEqual(chart_section["charts"][0]["data"]["matrix"][0], [9, 2])

        effect = next(section for section in result["sections"] if section["title"] == "输出结果3：效应量化分析")
        self.assertEqual(effect["rows"][0], ["q2", "0.298", "0.298", "0.285", "0.015"])
        self.assertEqual(effect["rows"][1], ["q3", "0.358", "0.358", "0.337", "0.000"])

    def test_legacy_var1_var2_params_still_work(self):
        result = chi_square_test(self.df, {"var1": "q1", "var2": "q2"})

        self.assertTrue(result["rows"])
        self.assertIn("q1 × q2", result["name"])


if __name__ == "__main__":
    unittest.main()
