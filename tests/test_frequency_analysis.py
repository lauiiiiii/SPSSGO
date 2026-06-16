# -*- coding: utf-8 -*-
import unittest

import pandas as pd

from backend.analysis.common import inject_frequency_metadata
from backend.analysis.methods.frequency import frequency_table


class FrequencyAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "q1": [1, 2, 2, 3, None],
                "q2": ["A", "A", "B", None, "B"],
            }
        )

    def test_legacy_single_variable_param_still_works(self):
        result = frequency_table(self.df, {"variable": "q1"})

        self.assertEqual(result["headers"], ["名称", "选项", "频数", "百分比(%)"])
        self.assertEqual(result["rows"][0], ["q1", "1.0", "1", "25.0"])
        self.assertEqual(result["rows"][-1], ["", "合计", "4", "100.0"])

    def test_multiple_variables_return_merged_table_and_charts(self):
        result = frequency_table(self.df, {"variables": ["q1", "q2"]})

        self.assertEqual(result["name"], "频数分析：q1、q2")
        self.assertIn(["q2", "A", "2", "50.0"], result["rows"])
        chart_section = next(section for section in result["sections"] if section["type"] == "charts")
        self.assertEqual(len(chart_section["charts"]), 2)
        self.assertEqual(chart_section["charts"][0]["chartType"], "category_distribution")
        self.assertEqual(chart_section["charts"][0]["data"]["total"], 4)
        self.assertEqual(chart_section["charts"][0]["data"]["fields"]["variable"], "q1")
        self.assertEqual(chart_section["charts"][0]["data"]["fields"]["x"], "q1")

    def test_value_labels_are_used(self):
        result = frequency_table(
            self.df,
            {
                "variables": ["q1"],
                "labels_by_variable": {"q1": {"1": "非常不同意", "2": "一般", "3": "非常同意"}},
            },
        )

        options = [row[1] for row in result["rows"]]
        self.assertIn("非常不同意", options)
        self.assertIn("一般", options)

    def test_frequency_metadata_injects_labels_for_each_variable(self):
        params = inject_frequency_metadata(
            {"variables": ["q1", "q2"]},
            {
                "q1": {"value_labels": {1: "低", 2: "中"}},
                "q2": {"value_labels": {"A": "甲", "B": "乙"}},
            },
        )

        self.assertEqual(params["labels_by_variable"]["q1"]["1"], "低")
        self.assertEqual(params["labels_by_variable"]["q2"]["A"], "甲")


if __name__ == "__main__":
    unittest.main()
