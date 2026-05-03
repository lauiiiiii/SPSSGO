# -*- coding: utf-8 -*-
"""
潜变量与因果方法校准脚本

目标：
1. 校验 PROCESS 风格方法是否输出 Bootstrap / 简单斜率等关键表；
2. 校验 AMOS / PLS-SEM 风格方法是否输出拟合、载荷、结构路径、效度等核心部分；
3. 作为后续高级方法回归测试的最小基线。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from backend.analysis import METHOD_REGISTRY


def build_dataset(n: int = 220) -> pd.DataFrame:
    rng = np.random.default_rng(20260410)
    x = rng.normal(0, 1, n)
    w = rng.normal(0, 1, n)
    m1 = 0.65 * x + rng.normal(0, 0.7, n)
    m2 = 0.45 * x + 0.50 * m1 + rng.normal(0, 0.7, n)
    y = 0.30 * x + 0.35 * m1 + 0.40 * m2 + 0.25 * x * w + rng.normal(0, 0.8, n)

    f1 = rng.normal(0, 1, n)
    f2 = 0.55 * f1 + rng.normal(0, 0.8, n)
    f3 = 0.40 * f1 + 0.50 * f2 + rng.normal(0, 0.8, n)

    df = pd.DataFrame({
        "x": x,
        "w": w,
        "m": m1,
        "m1": m1,
        "m2": m2,
        "y": y,
    })

    for idx in range(1, 4):
        df[f"f1_{idx}"] = 3 + 0.9 * f1 + rng.normal(0, 0.35, n)
        df[f"f2_{idx}"] = 3 + 0.9 * f2 + rng.normal(0, 0.35, n)
        df[f"f3_{idx}"] = 3 + 0.9 * f3 + rng.normal(0, 0.35, n)
    return df


def require_section(result: dict, title: str):
    for section in result.get("sections", []):
        if section.get("title") == title:
            return section
    raise AssertionError(f"missing section: {title}")


def main():
    df = build_dataset()

    mediation = METHOD_REGISTRY["mediation"](df, {"x": "x", "m": "m", "y": "y"})
    mediation_boot = require_section(mediation, "Bootstrap 间接效应检验")
    if mediation_boot["rows"][0][1] == "—":
        raise AssertionError("mediation bootstrap estimate missing")

    moderation = METHOD_REGISTRY["moderation"](df, {"x": "x", "w": "w", "y": "y"})
    simple_slopes = require_section(moderation, "简单斜率检验")
    if len(simple_slopes["rows"]) != 3:
        raise AssertionError("moderation simple slopes incomplete")

    parallel = METHOD_REGISTRY["parallel_mediation"](df, {"x": "x", "mediators": ["m1", "m2"], "y": "y"})
    require_section(parallel, "Bootstrap 特定间接效应")
    require_section(parallel, "Bootstrap 总间接效应")

    serial = METHOD_REGISTRY["serial_mediation"](df, {"x": "x", "mediators": ["m1", "m2"], "y": "y"})
    require_section(serial, "特定间接效应")
    require_section(serial, "链式间接效应 Bootstrap")

    path_result = METHOD_REGISTRY["path_analysis"](df, {"dependent": "y", "predictors": ["x", "m1", "m2"]})
    path_section = require_section(path_result, "标准化路径系数概览")
    if not path_section["rows"]:
        raise AssertionError("path analysis rows missing")

    cfa = METHOD_REGISTRY["confirmatory_factor_analysis"](
        df,
        {
            "factor1_vars": ["f1_1", "f1_2", "f1_3"],
            "factor2_vars": ["f2_1", "f2_2", "f2_3"],
            "factor3_vars": ["f3_1", "f3_2", "f3_3"],
        },
    )
    require_section(cfa, "输出结果5：模型拟合指标")
    require_section(cfa, "输出结果4：Pearson相关与AVE平方根值")
    require_section(cfa, "输出结果4-1：HTMT判据")

    sem = METHOD_REGISTRY["sem"](
        df,
        {
            "factor1_vars": ["f1_1", "f1_2", "f1_3"],
            "factor2_vars": ["f2_1", "f2_2", "f2_3"],
            "factor3_vars": ["f3_1", "f3_2", "f3_3"],
            "structural_paths": [
                {"dependent": "F2", "predictors": ["F1"]},
                {"dependent": "F3", "predictors": ["F1", "F2"]},
            ],
        },
    )
    require_section(sem, "模型拟合指标")
    require_section(sem, "测量模型载荷")
    require_section(sem, "结构路径系数")
    require_section(sem, "聚合效度与组合信度")
    require_section(sem, "HTMT 判据")
    require_section(sem, "Bootstrap 外部载荷稳定性")
    require_section(sem, "Bootstrap 路径显著性")
    require_section(sem, "直接效应/间接效应/总效应")
    require_section(sem, "Bootstrap 总效应稳定性")

    print("latent and causal calibration passed")


if __name__ == "__main__":
    main()
