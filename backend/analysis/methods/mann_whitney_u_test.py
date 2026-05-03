# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "mann_whitney_u_test"
METHOD_META = {'label': '独立样本MannWhitney检验',
 'category': '数据检验',
 'description': '比较两个独立组在秩次分布上的差异',
 'order': 40,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入二分类分组变量'},
           {'key': 'test_var', 'label': '检验变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入检验变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    group_var = params.get("group_var", "")
    test_var = params.get("test_var", "")
    if group_var not in df.columns or test_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量或检验变量不存在。"}
    temp = df[[group_var, test_var]].copy()
    temp[test_var] = pd.to_numeric(temp[test_var], errors="coerce")
    temp = temp.dropna()
    groups = list(pd.Series(temp[group_var]).dropna().unique())
    if len(groups) != 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Mann-Whitney 检验需要恰好 2 个组。"}
    g1 = temp.loc[temp[group_var] == groups[0], test_var]
    g2 = temp.loc[temp[group_var] == groups[1], test_var]
    stat, p_val = mannwhitneyu(g1, g2, alternative="two-sided")
    rows = [[str(groups[0]), str(len(g1)), _fmt(g1.median(), 4)], [str(groups[1]), str(len(g2)), _fmt(g2.median(), 4)]]
    sections = [
        _sec_table("组别描述", ["组别", "N", "中位数"], rows),
        _sec_table("Mann-Whitney 检验", ["U", "p"], [[_fmt(stat, 4), _fmt(p_val, 4)]]),
        _sec_advice("当两个独立样本不满足正态性或方差齐性假设时，可考虑使用 Mann-Whitney U 检验。"),
        _sec_smart(f"Mann-Whitney 检验完成，p 值为 {_fmt(p_val, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["组别", "N", "中位数"], "rows": rows, "description": "Mann-Whitney 检验完成。", "sections": sections}
