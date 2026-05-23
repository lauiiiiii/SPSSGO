from pathlib import Path
import json
import shutil
import subprocess
import uuid
from unittest.mock import patch

import pandas as pd
import pytest

from backend.analysis.methods import n_way_anova


def _sample_df():
    rows = []
    for a in ["A1", "A2"]:
        for b in ["B1", "B2", "B3"]:
            for c in ["C1", "C2"]:
                for rep in range(4):
                    rows.append({
                        "a": a,
                        "b": b,
                        "c": c,
                        "score": 2
                        + (a == "A2") * 0.8
                        + (b == "B2") * 0.3
                        + (b == "B3") * 0.6
                        + (c == "C2") * 0.4
                        + rep * 0.03,
                        "cov": rep,
                    })
    return pd.DataFrame(rows)


def test_n_way_anova_outputs_spssau_spsspro_style_sections():
    r_result = {
        "success": True,
        "name": "多因素方差分析",
        "headers": ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²", "η²", "partial η²"],
        "rows": [
            ["截距", "1.000", "1", "1.000", "10.000", "0.001**", "0.500", "0.450", "0.200", "0.300"],
            ["a", "0.500", "1", "0.500", "5.000", "0.030*", "", "", "0.100", "0.120"],
            ["b", "0.300", "2", "0.150", "1.500", "0.220", "", "", "0.060", "0.070"],
            ["c", "0.200", "1", "0.200", "2.000", "0.160", "", "", "0.040", "0.050"],
            ["误差", "4.000", "40", "0.100", "NaN", "NaN", "", "", "", ""],
        ],
        "description": "多因素方差分析完成。",
        "sections": [
            {"type": "advice", "title": "分析结果", "content": "多因素方差结果显示："},
            {"type": "advice", "title": "分析步骤", "content": "1. 可应用多因素方差分析"},
            {"type": "table", "title": "输出结果1：多因素方差分析结果", "headers": ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²", "η²", "partial η²"], "rows": [
                ["截距", "1.000", "1", "1.000", "10.000", "0.001**", "0.500", "0.450", "0.200", "0.300"],
                ["a", "0.500", "1", "0.500", "5.000", "0.030*", "", "", "0.100", "0.120"],
                ["b", "0.300", "2", "0.150", "1.500", "0.220", "", "", "0.060", "0.070"],
                ["c", "0.200", "1", "0.200", "2.000", "0.160", "", "", "0.040", "0.050"],
                ["误差", "4.000", "40", "0.100", "NaN", "NaN", "", "", "", ""],
            ]},
            {"type": "smart_analysis", "title": "智能分析", "content": "多因素方差结果显示："},
        ],
    }
    with patch("backend.analysis.methods.n_way_anova.is_r_runtime_available", return_value=True):
        with patch("backend.analysis.methods.n_way_anova.run_r_script", return_value=r_result) as run_r:
            result = n_way_anova.run(_sample_df(), {
                "factors": ["a", "b", "c"],
                "dependent": "score",
                "include_effect_size": True,
                "do_post_hoc": True,
                "post_hoc_method": "Bonferroni校正",
            })

    assert run_r.call_args.args[0] == "n_way_anova.R"
    assert "n_way_anova_input.csv" in run_r.call_args.kwargs["temp_files"]
    assert run_r.call_args.kwargs["payload"]["factors"] == ["a", "b", "c"]
    assert result["sections"][0]["title"] == "分析结果"
    assert result["sections"][1]["title"] == "分析步骤"
    main = result["sections"][2]
    assert main["title"] == "输出结果1：多因素方差分析结果"
    assert main["headers"] == ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²", "η²", "partial η²"]
    row_names = [row[0] for row in main["rows"]]
    assert row_names == ["截距", "a", "b", "c", "误差"]
    assert main["rows"][0][6]
    assert result["sections"][3]["title"] == "智能分析"
    assert not any(section["title"] == "各因素水平描述统计" for section in result["sections"])
    assert not any(section["title"] == "样本缺失情况汇总" for section in result["sections"])


def test_n_way_anova_can_skip_effect_size_and_post_hoc():
    r_result = {
        "success": True,
        "name": "多因素方差分析",
        "headers": ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²"],
        "rows": [
            ["截距", "1.000", "1", "1.000", "10.000", "0.001**", "0.500", "0.450"],
            ["a", "0.500", "1", "0.500", "5.000", "0.030*", "", ""],
            ["b", "0.300", "2", "0.150", "1.500", "0.220", "", ""],
            ["c", "0.200", "1", "0.200", "2.000", "0.160", "", ""],
            ["误差", "4.000", "40", "0.100", "NaN", "NaN", "", ""],
        ],
        "description": "多因素方差分析完成。",
        "sections": [
            {"type": "advice", "title": "分析结果", "content": "多因素方差结果显示："},
            {"type": "advice", "title": "分析步骤", "content": "1. 可应用多因素方差分析"},
            {"type": "table", "title": "输出结果1：多因素方差分析结果", "headers": ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²"], "rows": [
                ["截距", "1.000", "1", "1.000", "10.000", "0.001**", "0.500", "0.450"],
                ["a", "0.500", "1", "0.500", "5.000", "0.030*", "", ""],
                ["b", "0.300", "2", "0.150", "1.500", "0.220", "", ""],
                ["c", "0.200", "1", "0.200", "2.000", "0.160", "", ""],
                ["误差", "4.000", "40", "0.100", "NaN", "NaN", "", ""],
            ]},
            {"type": "smart_analysis", "title": "智能分析", "content": "多因素方差结果显示："},
        ],
    }
    with patch("backend.analysis.methods.n_way_anova.is_r_runtime_available", return_value=True):
        with patch("backend.analysis.methods.n_way_anova.run_r_script", return_value=r_result):
            result = n_way_anova.run(_sample_df(), {
                "factors": ["a", "b", "c"],
                "dependent": "score",
                "include_effect_size": False,
                "do_post_hoc": False,
            })

    main = result["sections"][2]
    assert main["headers"] == ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²"]
    assert main["rows"][0][0] == "截距"
    assert "a * b" not in [row[0] for row in main["rows"]]
    assert not any(section["title"] == "输出结果2：事后多重比较结果" for section in result["sections"])


def test_n_way_anova_requires_r_runtime():
    with patch("backend.analysis.methods.n_way_anova.is_r_runtime_available", return_value=False):
        result = n_way_anova.run(_sample_df(), {"factors": ["a", "b"], "dependent": "score"})

    assert "R 运行环境不可用" in result["description"]


def test_n_way_anova_r_script_keeps_spsspro_lsd_granularity():
    script = Path("backend/r_scripts/n_way_anova.R").read_text(encoding="utf-8")

    assert "drop_table <- stats::drop1(model, test = \"F\")" in script
    assert "intercept_coef[\"(Intercept)\", \"t value\"] ^ 2" in script
    assert "nrow(data) * mean(data[[dependent]])" not in script
    assert "welch_lsd_pair" in script
    assert "diff <- mean(group_i) - mean(group_j)" in script
    assert "stats::var(group_i) / n_i + stats::var(group_j) / n_j" in script
    assert "adjusted_lsd_pair" not in script
    assert "reference_grid" not in script
    assert "diff <- sum(contrast * beta)" not in script
    assert "se <- sqrt(ms_error * (1 / n_i + 1 / n_j))" not in script
    assert "model_coef" not in script
    assert "level_design" not in script


def _rscript_bin():
    found = shutil.which("Rscript")
    if found:
        return found
    bundled = Path("C:/Program Files/R/R-4.5.3/bin/Rscript.exe")
    return str(bundled) if bundled.exists() else None


def test_n_way_anova_r_script_uses_spsspro_raw_mean_posthoc_on_unbalanced_data():
    rscript = _rscript_bin()
    if not rscript:
        pytest.skip("Rscript is not available")

    rows = []
    counts = {
        ("A1", "B1", "C1"): 2,
        ("A1", "B1", "C2"): 2,
        ("A1", "B2", "C1"): 8,
        ("A1", "B2", "C2"): 8,
        ("A2", "B1", "C1"): 8,
        ("A2", "B1", "C2"): 8,
        ("A2", "B2", "C1"): 2,
        ("A2", "B2", "C2"): 2,
    }
    for (a, b, c), count in counts.items():
        for rep in range(count):
            noise = -0.1 if rep % 2 == 0 else 0.1
            rows.append({
                "a": a,
                "b": b,
                "c": c,
                "score": 10 + (a == "A2") * 2 + (b == "B2") * 10 + (c == "C2") * 1 + noise,
            })
    frame = pd.DataFrame(rows)
    raw_diff = frame.loc[frame["a"] == "A1", "score"].mean() - frame.loc[frame["a"] == "A2", "score"].mean()
    assert round(raw_diff, 3) != -2

    suffix = uuid.uuid4().hex
    data_path = Path(f"n_way_anova_input_{suffix}.csv")
    input_path = Path(f"n_way_anova_input_{suffix}.json")
    try:
        frame.to_csv(data_path, index=False)
        input_path.write_text(json.dumps({
            "factors": ["a", "b", "c"],
            "dependent": "score",
            "covariates": [],
            "do_post_hoc": True,
            "post_hoc_method": "LSD",
            "include_effect_size": False,
            "data_file": data_path.name,
        }, ensure_ascii=False), encoding="utf-8")

        completed = subprocess.run(
            [rscript, "backend/r_scripts/n_way_anova.R", "--input", str(input_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
    finally:
        data_path.unlink(missing_ok=True)
        input_path.unlink(missing_ok=True)
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    posthoc = next(section for section in result["sections"] if section["title"] == "输出结果2：事后多重比较结果")
    first, reverse = posthoc["rows"][:2]

    assert first[0:2] == ["A1", "A2"]
    assert reverse[0:2] == ["A2", "A1"]
    assert float(first[2]) == pytest.approx(raw_diff, abs=0.001)
    assert float(reverse[2]) == pytest.approx(-raw_diff, abs=0.001)
    assert first[3] == reverse[3]
    assert first[4] == reverse[4]
    assert float(first[5]) == pytest.approx(-float(reverse[6]), abs=0.001)
    assert float(first[6]) == pytest.approx(-float(reverse[5]), abs=0.001)
