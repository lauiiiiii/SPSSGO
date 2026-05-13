# -*- coding: utf-8 -*-
import unittest

import pandas as pd

from backend.analysis.methods.choice_multi_single import run as run_multi_single
from backend.analysis.methods.choice_single_multi import run as run_single_multi
from backend.analysis.registry import METHOD_META


class ChoiceMultiSingleAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "group": ["A", "A", "B", "B"],
            "q1": [2, 1, 2, 0],
            "q2": [0, 2, 2, 1],
        })

    def test_multi_single_count_value_supports_non_one_code(self):
        result = run_multi_single(self.df, {
            "single_var": "group",
            "multiple_vars": ["q1", "q2"],
            "count_value": "2",
        })

        self.assertEqual(result["headers"], ["多选项", "A", "B"])
        self.assertEqual(result["rows"], [
            ["q1", "50.0%", "50.0%"],
            ["q2", "50.0%", "50.0%"],
        ])

    def test_single_multi_count_value_supports_non_one_code(self):
        result = run_single_multi(self.df, {
            "single_var": "group",
            "multiple_vars": ["q1", "q2"],
            "count_value": "2",
        })

        self.assertEqual(result["headers"], ["单选结果", "q1", "q2"])
        self.assertEqual(result["rows"], [
            ["A", "50.0%", "50.0%"],
            ["B", "50.0%", "50.0%"],
        ])

    def test_both_methods_expose_count_value_option(self):
        expected_orders = {
            "choice_multi_single": 56,
            "choice_single_multi": 57,
        }
        for method_key, order in expected_orders.items():
            meta = METHOD_META[method_key]
            option = next(item for item in meta["options"] if item["key"] == "count_value")
            self.assertEqual(meta["category"], "问卷分析包")
            self.assertEqual(meta["order"], order)
            self.assertEqual(option["choices"], ["1", "2", "0"])
            self.assertEqual(option["default"], "1")


if __name__ == "__main__":
    unittest.main()
