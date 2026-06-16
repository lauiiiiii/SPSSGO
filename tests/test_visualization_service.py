# -*- coding: utf-8 -*-
import unittest

import pandas as pd
from fastapi import HTTPException

from backend.services.visualization_service import _build_chart


class VisualizationServiceTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "group": ["B", "A", "A", "B", None],
                "x": [1, 2, 3, None, 5],
                "y": [10, 20, None, 40, 50],
            }
        )

    def test_category_chart_counts_and_sorts(self):
        chart, warnings = _build_chart(self.df, "bar", {"x": "group"}, {})

        self.assertEqual(chart["chartType"], "category_distribution")
        self.assertEqual(chart["data"]["labels"], ["B", "A"])
        self.assertEqual(chart["data"]["counts"], [2, 2])
        self.assertEqual(chart["data"]["total"], 4)
        self.assertEqual(chart["data"]["fields"]["variable"], "group")
        self.assertIn("N=4", warnings[0])

    def test_histogram_uses_numeric_variable(self):
        chart, warnings = _build_chart(self.df, "histogram", {"x": "x"}, {"bins": 3})

        self.assertEqual(chart["chartType"], "histogram")
        self.assertEqual(len(chart["data"]["counts"]), 3)
        self.assertEqual(sum(chart["data"]["counts"]), 4)
        self.assertIn("N=4", warnings[0])

    def test_scatter_drops_pairwise_missing(self):
        chart, warnings = _build_chart(self.df, "scatter", {"x": "x", "y": "y"}, {})

        self.assertEqual(chart["chartType"], "scatter_plot")
        self.assertEqual(chart["data"]["total"], 3)
        self.assertEqual(chart["data"]["points"][0], {"x": 1.0, "y": 10.0})
        self.assertEqual(chart["data"]["fields"], {"x": "x", "y": "y"})
        self.assertEqual(chart["data"]["axisLabels"], {"x": "x", "y": "y"})
        self.assertIn("N=3", warnings[0])

    def test_invalid_variable_type_raises(self):
        with self.assertRaises(HTTPException) as ctx:
            _build_chart(self.df, "scatter", {"x": "group", "y": "y"}, {})

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("定量", str(ctx.exception.detail))


if __name__ == "__main__":
    unittest.main()
