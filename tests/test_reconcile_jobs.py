# -*- coding: utf-8 -*-
import unittest

from scripts.reconcile_jobs import classify_job


class ReconcileJobsTests(unittest.TestCase):
    def test_classify_completed_queued_job_as_succeeded(self):
        row = {
            "status": "queued",
            "created_at": 100.0,
            "started_at": 110.0,
            "finished_at": 120.0,
            "error_message": "",
        }
        decision = classify_job(row, now_ts=1000.0, older_than_seconds=60)
        self.assertIsNotNone(decision)
        self.assertEqual(decision.next_status, "succeeded")

    def test_classify_started_but_unfinished_queued_job_as_failed(self):
        row = {
            "status": "queued",
            "created_at": 100.0,
            "started_at": 110.0,
            "finished_at": None,
            "error_message": "",
        }
        decision = classify_job(row, now_ts=1000.0, older_than_seconds=60)
        self.assertIsNotNone(decision)
        self.assertEqual(decision.next_status, "failed")

    def test_ignore_recent_queued_job(self):
        row = {
            "status": "queued",
            "created_at": 980.0,
            "started_at": None,
            "finished_at": None,
            "error_message": "",
        }
        self.assertIsNone(classify_job(row, now_ts=1000.0, older_than_seconds=60))
