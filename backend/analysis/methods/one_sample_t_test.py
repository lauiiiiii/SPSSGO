# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "one_sample_t_test"
METHOD_META = {'label': '单样本T检验',
 'category': '差异对比分析包',
 'description': '检验样本均值是否显著偏离给定检验值',
 'order': 5,
 'slots': [{'key': 'test_vars', 'label': '检验变量', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入需要进行检验的变量'}],
 'options': [{'key': 'test_value', 'label': '检验值', 'choices': ['0', '1', '3', '5'], 'default': '0'}],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("test_vars", []) or params.get("variables", []))
    test_value = float(params.get("test_value", 0) or 0)
    if not variables:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 1 个检验变量。"}
    results = []
    for var in variables:
        series = pd.to_numeric(df[var], errors="coerce").dropna()
        if len(series) < 2:
            continue
        t_val, p_val = ttest_1samp(series, popmean=test_value)
        mean_diff = float(series.mean() - test_value)
        se = float(series.std(ddof=1) / np.sqrt(len(series))) if len(series) else np.nan
        crit = stats.t.ppf(0.975, len(series) - 1)
        ci_low = mean_diff - crit * se
        ci_high = mean_diff + crit * se
        results.append([var, str(len(series)), _fmt(series.mean(), 4), _fmt(test_value, 4), _fmt(mean_diff, 4), _fmt(t_val, 4), str(len(series) - 1), _fmt(p_val, 4), _fmt(ci_low, 4), _fmt(ci_high, 4)])
    sections = [
        _sec_table("单样本T检验结果", ["变量", "N", "样本均值", "检验值", "均值差", "t", "df", "p", "95% CI 下限", "95% CI 上限"], results),
        _sec_advice("单样本T检验适用于检验样本均值是否显著偏离某个理论值、标准值或目标值。"),
        _sec_smart(f"单样本T检验完成，共检验 {len(results)} 个变量。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["变量", "N", "样本均值", "检验值", "均值差", "t", "df", "p", "95% CI 下限", "95% CI 上限"], "rows": results, "description": f"单样本T检验完成，共检验 {len(results)} 个变量。", "sections": sections}
