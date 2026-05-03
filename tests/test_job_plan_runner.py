# -*- coding: utf-8 -*-
import unittest

from backend.services.jobs import plan_runner


class JobPlanRunnerTests(unittest.TestCase):
    def test_build_plan_execution_context_prefers_version_summary(self):
        column_meta = {"name": "x", "dtype": "int64", "missing": 0, "unique": 9}
        session = {
            "data_summary": '{"total_rows": 1, "total_cols": 1, "columns": [{"name": "old", "dtype": "int64", "missing": 0, "unique": 1}], "preview_rows": [{"old": 1}]}',
            "questionnaire_text": "q text",
            "research_topic": "topic",
            "variable_desc": "vars",
            "hypotheses": "hyp",
        }
        version = {"summary": {"total_rows": 9, "total_cols": 1, "columns": [column_meta], "preview_rows": [{"x": 1}]}}

        context = plan_runner.build_plan_execution_context(session, version, "do plan")

        self.assertEqual(context["plan"], "do plan")
        self.assertEqual(context["summary"]["total_rows"], 9)
        self.assertIn("研究主题: topic", context["research_info"])
