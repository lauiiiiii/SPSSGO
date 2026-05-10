import unittest

import pandas as pd

from backend.analysis.methods.normality_test import normality_test


class NormalityAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "q1_1": [1, 2, 3, 4, 5, 3, 4, 4, 5, 2, 3, 4],
            "q1_2": [2, 2, 3, 4, 5, 4, 4, 3, 5, 2, 3, 4],
        })

    def test_normality_analysis_outputs_combined_summary_and_extra_tests(self):
        result = normality_test(self.df, {"variables": ["q1_1", "q1_2"]})

        self.assertEqual(result["headers"], ["名称", "样本量", "中位数", "平均值", "标准差", "偏度", "峰度", "D值", "p", "W值", "p"])
        summary = result["sections"][0]
        self.assertEqual(summary["title"], "输出结果1：总体描述结果")
        self.assertEqual(summary["headerRows"][0][7]["text"], "Kolmogorov-Smirnov检验")
        self.assertEqual(summary["headerRows"][0][8]["text"], "Shapiro-Wilk检验")
        self.assertEqual(len(summary["rows"]), 2)

        titles = [section["title"] for section in result["sections"]]
        self.assertIn("Jarque-Bera检验", titles)
        self.assertIn("Anderson-darling检验", titles)

    def test_normality_analysis_outputs_hist_pp_qq_charts(self):
        result = normality_test(self.df, {"variables": ["q1_1"]})

        chart_sections = [section for section in result["sections"] if section["type"] == "charts"]
        chart_types = [chart_sections[index]["charts"][0]["chartType"] for index in range(len(chart_sections))]
        self.assertEqual(chart_types, ["normality_histogram", "pp_plot", "qq_plot"])


if __name__ == "__main__":
    unittest.main()
