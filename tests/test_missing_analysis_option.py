import unittest

import pandas as pd

from backend.analysis.common import append_optional_missing_analysis, build_slot_param_example
from backend.analysis.registry import METHOD_META
from backend.analysis.methods.frequency import frequency_table
from backend.analysis.methods.descriptive import descriptive


class MissingAnalysisOptionTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "q1": [1, 2, None, 3],
            "q2": [1, 1, 2, 2],
        })

    def test_common_missing_option_is_added_to_regular_methods(self):
        options = METHOD_META["frequency"]["options"]
        option = next(item for item in options if item["key"] == "include_missing_analysis")

        self.assertEqual(option["type"], "checkbox")
        self.assertFalse(option["default"])
        self.assertFalse(any(
            item.get("key") == "include_missing_analysis"
            for item in METHOD_META["descriptive"]["options"]
        ))

    def test_missing_table_only_appends_when_checked(self):
        result = frequency_table(self.df, {"variables": ["q1"]})
        result = append_optional_missing_analysis(result, self.df, {"variables": ["q1"]})
        self.assertFalse(any(
            section.get("title") == "缺失分析"
            for section in result["sections"]
        ))

        result = frequency_table(self.df, {"variables": ["q1"]})
        result = append_optional_missing_analysis(
            result,
            self.df,
            {"variables": ["q1"], "include_missing_analysis": True},
        )
        missing = next(section for section in result["sections"] if section["title"] == "缺失分析")
        self.assertEqual(missing["rows"][0][0], "q1")
        self.assertEqual(missing["rows"][0][2], "1")
        self.assertEqual(missing["rows"][0][3], "3")

    def test_descriptive_keeps_single_complete_missing_table(self):
        result = descriptive(self.df, {"variables": ["q1", "q2"]})
        result = append_optional_missing_analysis(
            result,
            self.df,
            {"variables": ["q1", "q2"], "include_missing_analysis": True},
        )

        self.assertEqual(
            sum(1 for section in result["sections"] if section.get("title") == "缺失分析"),
            1,
        )

    def test_slot_param_example_preserves_false_default(self):
        sample = build_slot_param_example({
            "slots": [],
            "options": [{"key": "save_efficiency", "type": "checkbox", "default": False}],
        })

        self.assertIs(sample["save_efficiency"], False)

    def test_missing_table_collects_directional_composite_variables(self):
        result = {
            "name": "方向型综合评价",
            "headers": [],
            "rows": [],
            "description": "ok",
            "sections": [],
        }

        result = append_optional_missing_analysis(
            result,
            self.df,
            {"positive_vars": ["q1"], "negative_vars": ["q2"], "include_missing_analysis": True},
        )

        missing = next(section for section in result["sections"] if section["title"] == "缺失分析")
        self.assertEqual([row[0] for row in missing["rows"]], ["q1", "q2"])

    def test_missing_table_collects_grey_relational_variables(self):
        result = {
            "name": "灰色关联分析",
            "headers": [],
            "rows": [],
            "description": "ok",
            "sections": [],
        }

        result = append_optional_missing_analysis(
            result,
            self.df,
            {"feature_vars": ["q1"], "mother_var": ["q2"], "include_missing_analysis": True},
        )

        missing = next(section for section in result["sections"] if section["title"] == "缺失分析")
        self.assertEqual([row[0] for row in missing["rows"]], ["q1", "q2"])

if __name__ == "__main__":
    unittest.main()
