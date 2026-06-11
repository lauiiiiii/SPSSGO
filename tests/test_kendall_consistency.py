import json
import shutil
import subprocess
import uuid
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from backend.analysis.methods import kendall_consistency


def _sample_df():
    return pd.DataFrame({
        "评委名": [f"评委{i}" for i in range(1, 11)],
        "景点1": [7, 9, 6, 7, 8, 4, 7, 8, 4, 7],
        "景点2": [8, 10, 9, 8, 6, 8, 8, 4, 6, 3],
        "景点3": [6, 7, 9, 9, 4, 10, 9, 5, 7, 9],
        "景点4": [8, 7, 7, 4, 8, 9, 8, 8, 2, 10],
        "景点5": [6, 6, 8, 9, 5, 8, 5, 9, 10, 8],
    })


def _rscript_bin():
    found = shutil.which("Rscript")
    if found:
        return found
    bundled = Path("C:/Program Files/R/R-4.5.3/bin/Rscript.exe")
    return str(bundled) if bundled.exists() else None


def test_kendall_consistency_uses_r_bridge():
    r_result = {
        "success": True,
        "name": "Kendall一致性检验_景点1_景点2_景点3",
        "headers": ["名称", "秩平均值", "中位数", "Kendall's W系数", "χ²", "P"],
        "rows": [["景点1", "2.5", "7", {"text": "0.049", "rowspan": 5}, {"text": "1.948", "rowspan": 5}, {"text": "0.745", "rowspan": 5}]],
        "description": "R bridge result",
        "sections": [{"type": "table", "title": "输出结果1：Kendall's W分析结果", "headers": [], "rows": []}],
    }

    with patch("backend.analysis.methods.kendall_consistency.is_r_runtime_available", return_value=True):
        with patch("backend.analysis.methods.kendall_consistency.run_r_script", return_value=r_result) as run_r:
            result = kendall_consistency.run(_sample_df(), {"variables": ["景点1", "景点2", "景点3", "景点4", "景点5"]})

    assert result["description"] == "R bridge result"
    assert run_r.call_args.args[0] == "kendall_consistency.R"
    assert run_r.call_args.kwargs["payload"]["variables"] == ["景点1", "景点2", "景点3", "景点4", "景点5"]
    csv_text = run_r.call_args.kwargs["temp_files"]["kendall_consistency_input.csv"]
    assert csv_text.splitlines()[0] == "景点1,景点2,景点3,景点4,景点5"


def test_kendall_consistency_requires_r_runtime():
    with patch("backend.analysis.methods.kendall_consistency.is_r_runtime_available", return_value=False):
        result = kendall_consistency.run(_sample_df(), {"variables": ["景点1", "景点2"]})

    assert "R 运行环境不可用" in result["description"]


def test_kendall_consistency_r_script_matches_spsspro_sample():
    rscript = _rscript_bin()
    if not rscript:
        pytest.skip("Rscript is not available")

    variables = ["景点1", "景点2", "景点3", "景点4", "景点5"]
    run_dir = Path("tmp_kendall_tests") / f"spssgo-kendall-test-{uuid.uuid4().hex}"
    run_dir.mkdir(parents=True, exist_ok=False)
    try:
        data_path = run_dir / "kendall_consistency_input.csv"
        input_path = run_dir / "input.json"
        _sample_df()[variables].to_csv(data_path, index=False)
        input_path.write_text(json.dumps({
            "variables": variables,
            "data_file": data_path.name,
        }, ensure_ascii=False), encoding="utf-8")

        completed = subprocess.run(
            [rscript, "backend/r_scripts/kendall_consistency.R", "--input", str(input_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kendall's W分析结果")

    assert main["headers"] == ["名称", "秩平均值", "中位数", "Kendall's W系数", "χ²", "P"]
    assert main["rows"][0][0:3] == ["景点1", "2.5", "7"]
    assert main["rows"][1][0:3] == ["景点2", "3.1", "8"]
    assert main["rows"][2][0:3] == ["景点3", "3.4", "8"]
    assert main["rows"][3][0:3] == ["景点4", "3.15", "8"]
    assert main["rows"][4][0:3] == ["景点5", "2.85", "8"]
    assert main["rows"][0][3] == {"text": "0.049", "rowspan": 5}
    assert main["rows"][0][4] == {"text": "1.948", "rowspan": 5}
    assert main["rows"][0][5] == {"text": "0.745", "rowspan": 5}
    assert "并列秩修正" in json.dumps(result["sections"][0]["rows"], ensure_ascii=False)
    refs = next(section for section in result["sections"] if section["title"] == "参考文献")
    assert not any("SPSSPRO" in item or "spsspro.com" in item for item in refs["items"])
