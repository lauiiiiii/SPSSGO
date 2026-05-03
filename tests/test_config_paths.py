# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

from backend import config


class ConfigPathTests(unittest.TestCase):
    def test_default_local_storage_root_stays_outside_backend_package(self):
        expected = Path(config.PROJECT_ROOT) / ".data"

        self.assertEqual(Path(config.LOCAL_STORAGE_ROOT), expected)
        self.assertNotEqual(Path(config.LOCAL_STORAGE_ROOT), Path(config.BASE_DIR))

