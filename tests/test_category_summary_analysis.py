import unittest

import pandas as pd

from backend.analysis.methods.category_summary import (
    METHOD_META,
    category_summary,
)


class CategorySummaryAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "group": [1, 1, 2, 2, 2, None],
            "q1": [2, 4, 3, 5, None, 9],
            "q2": [10, 20, 30, 40, 50, 60],
        })

    def test_category_summary_exposes_summary_type_option(self):
        option = next(
            item for item in METHOD_META["options"]
            if item["key"] == "summary_type"
        )
        self.assertEqual(option["type"], "multiple")
        self.assertEqual(option["default"], ["均值"])
        self.assertIn("计数", option["choices"])
        self.assertIn("求和", option["choices"])

    def test_category_summary_uses_selected_stat_type(self):
        result = category_summary(self.df, {
            "group_var": "group",
            "summary_vars": ["q1", "q2"],
            "summary_type": "计数",
            "group_labels": {"1": "A", "2": "B"},
        })
        self.assertEqual(result["headers"], ["标题", "A", "B", "汇总"])
        self.assertEqual(result["rows"], [["q1", "2", "2", "5"], ["q2", "2", "3", "6"]])
        self.assertEqual(result["sections"][0]["type"], "charts")
        chart = result["sections"][0]["charts"][0]
        self.assertEqual(chart["chartType"], "metric_comparison")
        self.assertEqual(chart["data"]["displayTitle"], "q1分类汇总")
        self.assertEqual(chart["data"]["defaultMode"], "bar")

    def test_category_summary_accepts_multiple_stat_types(self):
        result = category_summary(self.df, {
            "group_var": "group",
            "summary_vars": ["q1"],
            "summary_type": ["均值", "计数"],
            "group_labels": {"1": "A", "2": "B"},
        })
        self.assertEqual(result["headers"], ["标题", "A", "B", "汇总"])
        self.assertEqual(result["rows"], [["q1", "3.000", "4.000", "4.600"]])
        base = next(
            section for section in result["sections"]
            if section["title"] == "分类汇总分析结果-基础指标（平均值）"
        )
        self.assertEqual(base["headerRows"][0][1]["text"], "group")
        self.assertEqual(base["displayModes"][1]["label"], "计数")
        self.assertEqual(base["displayModes"][1]["rows"], [["q1", "2", "2", "5"]])
        charts = result["sections"][0]["charts"]
        self.assertEqual(len(charts), 1)
        self.assertEqual(charts[0]["data"]["displayTitle"], "q1分类汇总")
        self.assertIn("均值", charts[0]["data"]["metrics"])

    def test_category_summary_outputs_filterable_detail_table(self):
        result = category_summary(self.df, {
            "group_var": "group",
            "summary_vars": ["q1"],
            "summary_type": ["均值"],
            "group_labels": {"1": "A", "2": "B"},
        })
        detail = next(
            section for section in result["sections"]
            if section["title"] == "输出结果3：详细指标表"
        )
        self.assertEqual(detail["headers"], ["标题", "项", "A", "B", "汇总"])
        self.assertEqual(detail["headerRows"][0][2]["text"], "group")
        self.assertEqual(detail["headerRows"][0][2]["colspan"], 2)
        self.assertEqual(detail["rowFilter"]["columnIndex"], 1)
        self.assertIn("99分位数", detail["rowFilter"]["choices"])
        self.assertEqual(detail["bodyRowspanColumns"], 1)
        self.assertEqual(detail["rows"][0][0], {"text": "q1", "rowspan": 21})
        self.assertIn(["q1", "n", "2", "2", "5"], detail["exportRows"])
        self.assertTrue(any(row[1] == "均值95% CI(LL)" for row in detail["exportRows"]))

    def test_category_summary_excludes_group_var_from_summary_vars(self):
        result = category_summary(self.df, {
            "group_var": "group",
            "summary_vars": ["group", "q1"],
            "summary_type": ["均值"],
            "group_labels": {"1": "A", "2": "B"},
        })
        self.assertEqual(result["rows"], [["q1", "3.000", "4.000", "4.600"]])


if __name__ == "__main__":
    unittest.main()
