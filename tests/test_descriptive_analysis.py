import unittest

import numpy as np
import pandas as pd

from backend.analysis.methods.descriptive import descriptive


class DescriptiveAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "q1": [1, 2, 3, 4, 5, np.nan],
            "q2": [2, 2, 4, 4, 5, 5],
        })

    def test_descriptive_returns_deep_metrics_and_percentiles(self):
        result = descriptive(self.df, {"variables": ["q1", "q2"]})
        titles = [section["title"] for section in result["sections"]]

        self.assertIn("输出结果3：深入指标", titles)
        self.assertIn("百分位数", titles)

        deep = next(section for section in result["sections"] if section["title"] == "输出结果3：深入指标")
        self.assertIn("均值95% CI(LL)", deep["headers"])
        self.assertIn("变异系数(CV)", deep["headers"])

        percentile = next(section for section in result["sections"] if section["title"] == "百分位数")
        self.assertIn("P2.5", percentile["headers"])
        self.assertIn("P97.5", percentile["headers"])
        self.assertEqual(len(percentile["rows"]), 2)

    def test_descriptive_returns_mean_comparison_chart(self):
        result = descriptive(self.df, {"variables": ["q1", "q2"]})
        chart_section = next(section for section in result["sections"] if section["title"] == "输出结果2：平均值对比图")

        self.assertEqual(chart_section["charts"][0]["chartType"], "metric_comparison")
        self.assertEqual(chart_section["charts"][0]["data"]["metric"], "平均值")
        self.assertEqual(chart_section["charts"][0]["data"]["labels"], ["q1", "q2"])
        self.assertEqual(chart_section["charts"][0]["data"]["fields"]["value"], "平均值")
        self.assertEqual(chart_section["charts"][0]["data"]["axisLabels"]["y"], "平均值")

    def test_descriptive_returns_variable_missing_table(self):
        result = descriptive(self.df, {"variables": ["q1", "q2"]})
        missing = next(section for section in result["sections"] if section["title"] == "缺失分析")

        self.assertEqual(missing["rows"][0][0], "q1")
        self.assertEqual(missing["rows"][0][2], "1")
        self.assertEqual(missing["rows"][0][3], "6")
        self.assertEqual(missing["rows"][1][3], "无")


if __name__ == "__main__":
    unittest.main()
