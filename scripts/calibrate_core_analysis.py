# -*- coding: utf-8 -*-
"""
核心学术方法校准脚本

目标：
1. 固定 10 个基础方法的统计口径；
2. 用 scipy / statsmodels / factor_analyzer 的标准实现做交叉校验；
3. 作为后续回归测试的最小基线。
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
from scipy.stats import chi2_contingency, f_oneway, levene, pearsonr, ttest_ind, ttest_rel

from backend.analysis import METHOD_REGISTRY, build_execute_params


def build_dataset(n: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(20260410)
    df = pd.DataFrame({
        "group2": rng.choice([1, 2], n),
        "group3": rng.choice([1, 2, 3], n, p=[0.3, 0.35, 0.35]),
        "cat1": rng.choice(["A", "B", "C"], n),
        "cat2": rng.choice(["X", "Y"], n),
        "x1": rng.normal(50, 8, n),
        "x2": rng.normal(55, 9, n),
        "x3": rng.normal(60, 10, n),
        "y": rng.normal(70, 6, n),
    })

    df["score"] = 0.45 * df["x1"] + 0.25 * df["x2"] - 0.15 * df["x3"] + rng.normal(0, 4, n)
    df["paired1"] = rng.normal(30, 5, n)
    df["paired2"] = df["paired1"] + rng.normal(1.2, 2.2, n)

    for i in range(1, 6):
        latent = rng.normal(0, 1, n)
        df[f"item{i}"] = np.clip(np.round(3 + 0.9 * latent + rng.normal(0, 0.7, n)), 1, 5)

    return df


def assert_close(actual: float, expected: float, tol: float, label: str):
    if math.isnan(actual) and math.isnan(expected):
        return
    if abs(actual - expected) > tol:
        raise AssertionError(f"{label} mismatch: actual={actual}, expected={expected}, tol={tol}")


def get_table_value(section: dict, row_name: str, value_col: int = 1) -> float:
    for row in section.get("rows", []):
        if row and str(row[0]) == row_name:
            return float(str(row[value_col]).replace("%", ""))
    raise KeyError(row_name)


def main():
    df = build_dataset()

    # 描述性统计
    desc = METHOD_REGISTRY["descriptive"](df, {"variables": ["x1"]})
    desc_row = desc["rows"][0]
    assert_close(float(desc_row[2]), float(df["x1"].mean()), 1e-3, "descriptive mean")
    assert_close(float(desc_row[3]), float(df["x1"].std(ddof=1)), 1e-3, "descriptive std")

    # 信度分析
    rel = METHOD_REGISTRY["reliability"](df, build_execute_params("reliability", {"variables": ["item1", "item2", "item3", "item4"]}))
    rel_alpha = float(rel["rows"][0][0])
    rel_data = df[["item1", "item2", "item3", "item4"]].apply(pd.to_numeric, errors="coerce").dropna()
    k = rel_data.shape[1]
    expected_alpha = (k / (k - 1)) * (1 - rel_data.var(ddof=1).sum() / rel_data.sum(axis=1).var(ddof=1))
    assert_close(rel_alpha, expected_alpha, 1e-3, "cronbach alpha")

    # 效度分析
    fac = METHOD_REGISTRY["factor_analysis"](df, build_execute_params("factor_analysis", {"variables": ["item1", "item2", "item3", "item4"]}))
    fac_table = fac["sections"][0]
    fac_data = df[["item1", "item2", "item3", "item4"]].apply(pd.to_numeric, errors="coerce").dropna()
    _, kmo_total = calculate_kmo(fac_data)
    chi2, p = calculate_bartlett_sphericity(fac_data)
    assert_close(get_table_value(fac_table, "KMO"), float(kmo_total), 1e-3, "kmo")
    assert_close(get_table_value(fac_table, "Bartlett球形检验 χ²"), float(chi2), 1e-2, "bartlett chi2")
    assert_close(get_table_value(fac_table, "Bartlett球形检验 p"), float(p), 1e-3, "bartlett p")

    # 独立样本 t 检验
    ind = METHOD_REGISTRY["independent_t_test"](df, build_execute_params("independent_t_test", {"group_var": "group2", "test_vars": ["x1"]}))
    ind_t_section = next(sec for sec in ind["sections"] if sec["title"] == "独立样本t检验")
    g1 = df.loc[df["group2"] == 1, "x1"].dropna()
    g2 = df.loc[df["group2"] == 2, "x1"].dropna()
    lev_f, lev_p = levene(g1, g2, center="mean")
    t_expected, p_expected = ttest_ind(g1, g2, equal_var=(lev_p > 0.05))
    chosen_row = ind_t_section["rows"][0] if lev_p > 0.05 else ind_t_section["rows"][1]
    assert_close(float(chosen_row[1]), float(t_expected), 1e-3, "independent t")
    assert_close(float(chosen_row[3]), float(p_expected), 1e-3, "independent t p")

    # 配对样本 t 检验
    paired = METHOD_REGISTRY["paired_t_test"](df, {"var1": "paired1", "var2": "paired2"})
    paired_section = next(sec for sec in paired["sections"] if sec["title"] == "输出结果3：配对样本T检验结果")
    t_expected, p_expected = ttest_rel(df["paired1"], df["paired2"])
    assert_close(float(paired_section["rows"][0][4]), float(t_expected), 1e-2, "paired t")
    assert_close(float(str(paired_section["rows"][0][6]).rstrip("*")), float(p_expected), 1e-3, "paired p")

    # 单因素方差分析
    anova = METHOD_REGISTRY["anova_oneway"](df, build_execute_params("anova_oneway", {"group_var": "group3", "test_vars": ["x2"], "post_hoc": "Bonferroni"}))
    anova_section = next(sec for sec in anova["sections"] if sec["title"] == "方差分析表")
    groups = [df.loc[df["group3"] == g, "x2"].dropna() for g in sorted(df["group3"].unique())]
    f_expected, p_expected = f_oneway(*groups)
    assert_close(float(anova_section["rows"][0][4]), float(f_expected), 1e-2, "anova F")
    assert_close(float(anova_section["rows"][0][5]), float(p_expected), 1e-3, "anova p")

    # 卡方检验
    chi = METHOD_REGISTRY["chi_square"](df, {"var1": "cat1", "var2": "cat2"})
    chi_section = next(sec for sec in chi["sections"] if sec["title"] == "输出结果1：卡方检验分析结果")
    ct = pd.crosstab(df["cat1"], df["cat2"])
    chi2, p, _, _ = chi2_contingency(ct, correction=False)
    assert_close(float(chi_section["rows"][0][-2]["text"]), float(chi2), 1e-3, "chi-square")
    assert_close(float(chi_section["rows"][0][-1]["text"].replace("*", "")), float(p), 1e-3, "chi-square p")

    # Pearson 相关
    corr = METHOD_REGISTRY["pearson_correlation"](df, {"variables": ["x1", "x2"]})
    corr_r = float(str(corr["rows"][0][4]).replace("*", ""))
    expected_r, _ = pearsonr(df["x1"], df["x2"])
    assert_close(corr_r, float(expected_r), 1e-3, "pearson r")

    # 多元线性回归
    reg = METHOD_REGISTRY["multiple_regression"](df, build_execute_params("multiple_regression", {"dependent": "score", "predictors": ["x1", "x2", "x3"]}))
    reg_section = next(sec for sec in reg["sections"] if sec["title"] == "模型摘要")
    X = sm.add_constant(df[["x1", "x2", "x3"]])
    model = sm.OLS(df["score"], X).fit()
    assert_close(float(reg_section["rows"][0][1]), float(model.rsquared), 1e-3, "regression R2")
    assert_close(float(reg_section["rows"][0][2]), float(model.rsquared_adj), 1e-3, "regression adjR2")

    # 验证性因子分析
    cfa = METHOD_REGISTRY["confirmatory_factor_analysis"](df, {"factor1_vars": ["item1", "item2"], "factor2_vars": ["item3", "item4", "item5"]})
    if not cfa.get("sections"):
        raise AssertionError("cfa returned no sections")

    print("core calibration passed")


if __name__ == "__main__":
    main()
