# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "one_sample_wilcoxon"
METHOD_META = {'label': '单样本Wilcoxon符号秩检验',
 'category': '数据检验',
 'description': '检验样本中位数是否显著偏离给定检验值',
 'order': 30,
 'slots': [{'key': 'variable', 'label': '检验变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入需要检验的变量'}],
 'options': [{'key': 'test_value', 'label': '检验值', 'choices': ['0', '1', '3', '5'], 'default': '0'}],
 'param_builder': 'direct'}


def run(df, params):
    variable = params.get("variable", "")
    test_value = float(params.get("test_value", 0) or 0)
    if variable not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "检验变量不存在。"}
    series = pd.to_numeric(df[variable], errors="coerce").dropna()
    diff = series - test_value
    diff = diff[diff != 0]
    if len(diff) < 1:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "没有足够的非零差值样本。"}
    stat, p_val = wilcoxon(diff)
    rows = [[variable, str(len(diff)), _fmt(series.median(), 4), _fmt(test_value, 4), _fmt(stat, 4), _fmt(p_val, 4)]]
    sections = [
        _sec_table("单样本Wilcoxon结果", ["变量", "N", "样本中位数", "检验值", "W", "p"], rows),
        _sec_advice("当数据不满足正态性假设时，可用单样本 Wilcoxon 符号秩检验替代单样本T检验。"),
        _sec_smart(f"单样本 Wilcoxon 检验完成，变量 {variable} 的 p 值为 {_fmt(p_val, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["变量", "N", "样本中位数", "检验值", "W", "p"], "rows": rows, "description": f"单样本 Wilcoxon 检验完成。", "sections": sections}
