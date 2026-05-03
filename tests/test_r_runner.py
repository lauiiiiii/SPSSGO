# -*- coding: utf-8 -*-
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from backend import r_runner


class _FakeTempDirectory:
    def __init__(self, path: str):
        self.path = path

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc, tb):
        return False


class RRunnerTests(unittest.TestCase):
    def test_is_r_runtime_available_requires_feature_flag(self):
        with patch("backend.r_runner.R_ENABLED", False):
            with patch("backend.r_runner.shutil.which", return_value="C:\\R\\bin\\Rscript.exe"):
                self.assertFalse(r_runner.is_r_runtime_available())

    def test_run_r_script_raises_when_disabled(self):
        with patch("backend.r_runner.R_ENABLED", False):
            with self.assertRaises(r_runner.RExecutionError):
                r_runner.run_r_script("health_check.R")

    def test_get_r_script_path_rejects_missing_script(self):
        with self.assertRaises(r_runner.RExecutionError):
            r_runner.get_r_script_path("missing.R")

    def test_run_r_script_parses_json_stdout(self):
        completed = Mock(returncode=0, stdout=json.dumps({"success": True, "engine": "R"}), stderr="")
        temp_dir = _FakeTempDirectory(str(Path(__file__).resolve().parent))
        with patch("backend.r_runner.R_ENABLED", True):
            with patch("backend.r_runner.tempfile.TemporaryDirectory", return_value=temp_dir):
                with patch("backend.r_runner.subprocess.run", return_value=completed) as run_mock:
                    result = r_runner.run_r_script("health_check.R")

        self.assertEqual(result["engine"], "R")
        command = run_mock.call_args.args[0]
        self.assertEqual(command[0], r_runner.RSCRIPT_BIN)
        self.assertEqual(Path(command[1]).name, "health_check.R")

    def test_run_r_script_accepts_relative_temp_dir(self):
        completed = Mock(returncode=0, stdout=json.dumps({"success": True}), stderr="")
        temp_path = (Path(".tmp") / "r-runner-test").resolve()
        with patch("backend.r_runner.R_ENABLED", True):
            with patch("backend.r_runner._create_temp_dir", return_value=temp_path):
                with patch("backend.r_runner._cleanup_temp_dir"):
                    with patch.object(Path, "mkdir"):
                        with patch.object(Path, "write_text"):
                            with patch("backend.r_runner.subprocess.run", return_value=completed):
                                result = r_runner.run_r_script(
                                    "health_check.R",
                                    payload={"data_file": "input.csv"},
                                    temp_files={"input.csv": "a,b\n1,2\n"},
                                )

        self.assertTrue(result["success"])

    def test_create_temp_dir_resolves_relative_base(self):
        with patch("backend.r_runner.R_TEMP_DIR", ".tmp/r-runner-test"):
            with patch("backend.r_runner.uuid.uuid4", return_value=Mock(hex="abcdef123456")):
                with patch.object(Path, "mkdir"):
                    temp_path = r_runner._create_temp_dir()

        self.assertTrue(temp_path.is_absolute())
        self.assertEqual(temp_path.name, "spssgo-r-abcdef1234")

    def test_run_r_script_raises_on_non_zero_exit(self):
        completed = Mock(returncode=1, stdout="", stderr="package not found")
        temp_dir = _FakeTempDirectory(str(Path(__file__).resolve().parent))
        with patch("backend.r_runner.R_ENABLED", True):
            with patch("backend.r_runner.tempfile.TemporaryDirectory", return_value=temp_dir):
                with patch("backend.r_runner.subprocess.run", return_value=completed):
                    with self.assertRaises(r_runner.RExecutionError) as ctx:
                        r_runner.run_r_script("health_check.R")

        self.assertIn("package not found", str(ctx.exception))
