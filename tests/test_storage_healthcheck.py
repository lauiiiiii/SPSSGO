# -*- coding: utf-8 -*-
import shutil
import unittest
from pathlib import Path

from backend.storage.local import LocalStorage


class LocalStorageHealthcheckTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("tests/.tmp/storage-healthcheck")
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_healthcheck_reports_writable_root(self):
        storage = LocalStorage(str(self.temp_dir))

        result = storage.healthcheck()

        self.assertTrue(result["ok"])
        self.assertEqual(result["backend"], "local")
        self.assertEqual(result["root_dir"], str(self.temp_dir))
        self.assertTrue(self.temp_dir.exists())
        self.assertTrue((self.temp_dir / "uploads").exists())
        self.assertTrue((self.temp_dir / "outputs").exists())
        self.assertTrue((self.temp_dir / "datasets").exists())
        self.assertTrue((self.temp_dir / ".cache").exists())
