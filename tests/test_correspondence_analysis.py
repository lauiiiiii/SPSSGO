import unittest

import pandas as pd

from backend.analysis.methods.correspondence_analysis import METHOD_META, run


class CorrespondenceAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "gender": ["男", "男", "女", "女", "男", "女", "男", "女"],
            "choice": ["A", "B", "A", "B", "A", "B", "B", "A"],
            "region": ["东部", "东部", "西部", "西部", "东部", "西部", "西部", "东部"],
        })

    def test_meta_uses_spsspro_style_single_multiple_slot(self):
        slots = METHOD_META["slots"]
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]["key"], "variables")
        self.assertEqual(slots[0]["type"], "multiple")
        self.assertEqual(slots[0]["accept"], "categorical")
        self.assertEqual(slots[0]["min"], 2)

    def test_two_variable_correspondence_outputs_core_tables_and_chart(self):
        result = run(self.df, {"variables": ["gender", "choice"]})

        self.assertIn("gender × choice", result["name"])
        section_titles = [section["title"] for section in result["sections"]]
        self.assertIn("输出结果1：模型汇总", section_titles)
        self.assertIn("输出结果2：维度得分", section_titles)
        self.assertIn("输出结果3：维度对应图", section_titles)
        score_section = next(section for section in result["sections"] if section["title"] == "输出结果2：维度得分")
        self.assertEqual(score_section["headers"][:3], ["字段名", "项", "维度1"])
        chart_section = next(section for section in result["sections"] if section["title"] == "输出结果3：维度对应图")
        self.assertEqual(chart_section["charts"][0]["chartType"], "correspondence_map")

    def test_legacy_var1_var2_params_still_work(self):
        result = run(self.df, {"var1": "gender", "var2": "choice"})

        self.assertIn("gender × choice", result["name"])
        self.assertTrue(result["rows"])

    def test_multiple_variables_use_mca_style_category_map(self):
        result = run(self.df, {"variables": ["gender", "choice", "region"]})

        self.assertIn("gender、choice、region", result["name"])
        section_titles = [section["title"] for section in result["sections"]]
        self.assertIn("输出结果1：模型汇总", section_titles)
        self.assertIn("输出结果2：维度得分", section_titles)
        summary_section = next(section for section in result["sections"] if section["title"] == "输出结果1：模型汇总")
        self.assertEqual(summary_section["headers"], ["维度", "奇异值", "特征根值(惯量)", "解释率", "累积解释率"])
        score_section = next(section for section in result["sections"] if section["title"] == "输出结果2：维度得分")
        self.assertNotIn("质量", score_section["headers"])
        chart_section = next(section for section in result["sections"] if section["title"] == "输出结果3：维度对应图")
        chart = chart_section["charts"][0]
        self.assertEqual(chart["chartType"], "correspondence_map")
        self.assertEqual(set(chart["data"]["series"]), {"gender", "choice", "region"})


if __name__ == "__main__":
    unittest.main()
