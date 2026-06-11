# -*- coding: utf-8 -*-
import json
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
R_SCRIPT = PROJECT_ROOT / "backend" / "r_scripts" / "intraclass_correlation.R"
SAMPLE_FILE = Path(r"C:\Users\Administrator.DESKTOP-854VSP0\Downloads\组内相关系数.xlsx")


def _rscript_bin():
    bundled = Path(r"C:\Program Files\R\R-4.5.3\bin\Rscript.exe")
    if bundled.exists():
        return str(bundled)
    return shutil.which("Rscript")


class IntraclassCorrelationScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rscript = _rscript_bin()
        if not cls.rscript:
            raise unittest.SkipTest("Rscript 不可用，跳过 ICC R 脚本测试")
        if not SAMPLE_FILE.exists():
            raise unittest.SkipTest("缺少组内相关系数.xlsx样例数据，跳过 ICC R 脚本测试")
        try:
            cls.data = pd.read_excel(SAMPLE_FILE)
        except ImportError as exc:
            raise unittest.SkipTest(f"缺少 xlsx 读取依赖：{exc}") from exc

    def _run_icc(self, variables, icc_type):
        work_dir = Path(tempfile.gettempdir()) / f"spssgo-icc-test-{uuid.uuid4().hex[:10]}"
        work_dir.mkdir(parents=True, exist_ok=False)
        try:
            csv_path = work_dir / "intraclass_correlation_input.csv"
            input_path = work_dir / "input.json"
            self.data[variables].to_csv(csv_path, index=False, encoding="utf-8")
            input_path.write_text(
                json.dumps(
                    {
                        "variables": variables,
                        "icc_type": icc_type,
                        "data_file": "intraclass_correlation_input.csv",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [self.rscript, str(R_SCRIPT), "--input", str(input_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
            result = json.loads(completed.stdout)
            self.assertTrue(result.get("success"), result)
            return result
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def _assert_row(self, row, label, icc, lower, upper, f_value, df1, df2, p_text):
        self.assertEqual(row[0], label)
        self.assertAlmostEqual(float(row[1]), icc, places=3)
        self.assertAlmostEqual(float(row[2]), lower, places=3)
        self.assertAlmostEqual(float(row[3]), upper, places=3)
        self.assertAlmostEqual(float(row[4]), f_value, places=3)
        self.assertEqual(row[5], str(df1))
        self.assertEqual(row[6], str(df2))
        self.assertEqual(row[7], p_text)

    def test_selected_icc_types_include_id_as_normal_numeric_column(self):
        variables = list(self.data.columns)
        cases = [
            (
                "双向混合/随机 一致性",
                "双向混合/随机 一致性",
                ("单一度量ICC(C,1)", 0.215, 0.140, 0.306, 2.640, 99, 495, "0.000****"),
                ("平均度量ICC(C,K)", 0.621, 0.493, 0.726, 2.640, 99, 495, "0.000****"),
            ),
            (
                "双向混合/随机 绝对一致性",
                "双向混合/随机 绝对一致性",
                ("单一度量ICC(A,1)", 0.121, 0.055, 0.205, 2.640, 99, 495, "0.000****"),
                ("平均度量ICC(A,K)", 0.453, 0.259, 0.607, 2.640, 99, 495, "0.000****"),
            ),
            (
                "单向随机 绝对一致性",
                "单向随机 绝对一致性",
                ("单一度量ICC(1)", 0.053, -0.000, 0.123, 1.336, 99, 500, "0.025**"),
                ("平均度量ICC(K)", 0.251, -0.001, 0.458, 1.336, 99, 500, "0.025**"),
            ),
        ]
        for icc_type, group_title, single, average in cases:
            with self.subTest(icc_type=icc_type):
                result = self._run_icc(variables, icc_type)
                rows = result["rows"]
                self.assertEqual(len(rows), 2)
                self.assertEqual(result["meta"]["valid_n"], 100)
                self.assertEqual(result["meta"]["variable_count"], 6)
                self.assertEqual(result["sections"][1]["headerRows"][0][0]["text"], group_title)
                self._assert_row(rows[0], *single)
                self._assert_row(rows[1], *average)

    def test_rating_columns_only_keep_high_reliability_result(self):
        variables = list(self.data.columns[1:])
        result = self._run_icc(variables, "双向混合/随机 绝对一致性")
        rows = result["rows"]

        self.assertEqual(result["meta"]["valid_n"], 100)
        self.assertEqual(result["meta"]["variable_count"], 5)
        self.assertEqual(rows[0][0], "单一度量ICC(A,1)")
        self.assertEqual(rows[1][0], "平均度量ICC(A,K)")
        self.assertAlmostEqual(float(rows[0][1]), 0.957, places=3)
        self.assertAlmostEqual(float(rows[1][1]), 0.991, places=3)

    def test_legacy_english_icc_type_remains_supported(self):
        variables = list(self.data.columns)
        result = self._run_icc(variables, "Two-way random/mixed consistency")

        self.assertEqual(result["sections"][1]["headerRows"][0][0]["text"], "双向混合/随机 一致性")
        self.assertEqual(result["meta"]["icc_type"], "双向混合/随机 一致性")
        self.assertAlmostEqual(float(result["rows"][0][1]), 0.215, places=3)


if __name__ == "__main__":
    unittest.main()
