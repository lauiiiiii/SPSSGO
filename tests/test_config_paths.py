# -*- coding: utf-8 -*-
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


class ConfigPathTests(unittest.TestCase):
    def test_default_local_storage_root_stays_outside_backend_package(self):
        env_key = "LOCAL_STORAGE_ROOT"
        old_value = os.environ.pop(env_key, None)

        # 计算 .env 路径，mock 掉它让 config 加载不到外部配置
        test_dir = Path(__file__).resolve().parent
        project_root = test_dir.parent
        dotenv_path = str(project_root / ".env")

        # 清理已导入的 backend 模块缓存，强制重新加载
        for mod in list(sys.modules.keys()):
            if mod.startswith("backend"):
                del sys.modules[mod]

        original_exists = os.path.exists

        def mock_exists(path):
            if str(path) == dotenv_path:
                return False
            return original_exists(path)

        with patch("os.path.exists", side_effect=mock_exists):
            from backend import config

        expected = Path(config.PROJECT_ROOT) / ".data"
        try:
            self.assertEqual(Path(config.LOCAL_STORAGE_ROOT), expected)
            self.assertNotEqual(Path(config.LOCAL_STORAGE_ROOT), Path(config.BASE_DIR))
        finally:
            if old_value is not None:
                os.environ[env_key] = old_value
