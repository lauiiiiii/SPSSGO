# -*- coding: utf-8 -*-
import json
import os
import shutil
import time
import unittest
from pathlib import Path

from scripts.apply_s3_lifecycle import load_config
from scripts.backup_mysql import prune_old_backups, resolve_output_path


class BackupMysqlScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("tests/.tmp/ops-scripts")
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_resolve_output_path_uses_gzip_suffix(self):
        class Args:
            output_dir = str(self.temp_dir)
            filename = ""
            gzip = True
            database = "demo"

        output = resolve_output_path(Args())

        self.assertEqual(output.parent, self.temp_dir)
        self.assertTrue(output.name.endswith(".sql.gz"))

    def test_prune_old_backups_removes_expired_files(self):
        old_file = self.temp_dir / "old.sql"
        new_file = self.temp_dir / "new.sql"
        old_file.write_text("old", encoding="utf-8")
        new_file.write_text("new", encoding="utf-8")

        cutoff_time = time.time() - 10 * 24 * 3600
        os.utime(old_file, (cutoff_time, cutoff_time))

        removed = prune_old_backups(self.temp_dir, retention_days=7)

        self.assertIn(old_file, removed)
        self.assertFalse(old_file.exists())
        self.assertTrue(new_file.exists())


class ApplyS3LifecycleScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("tests/.tmp/ops-lifecycle")
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_config_accepts_rules_array(self):
        config_path = self.temp_dir / "lifecycle.json"
        config_path.write_text(json.dumps({"Rules": [{"ID": "demo", "Status": "Enabled"}]}), encoding="utf-8")

        loaded = load_config(str(config_path))

        self.assertEqual(loaded["Rules"][0]["ID"], "demo")

    def test_load_config_rejects_missing_rules(self):
        config_path = self.temp_dir / "invalid.json"
        config_path.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_config(str(config_path))
