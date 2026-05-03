# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "kruskal_wallis_test"
METHOD_META = {'label': '多独立样本Kruskal-Wallis检验',
 'category': '数据检验',
 'description': '比较三个及以上独立组在秩次分布上的差异',
 'order': 45,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入分组变量（3组及以上）'},
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
    if len(groups) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Kruskal-Wallis 检验至少需要 3 个组。"}
    samples = [temp.loc[temp[group_var] == g, test_var] for g in groups]
    stat, p_val = kruskal(*samples)
    desc_rows = [[str(g), str(len(s)), _fmt(s.median(), 4)] for g, s in zip(groups, samples)]
    sections = [
        _sec_table("组别描述", ["组别", "N", "中位数"], desc_rows),
        _sec_table("Kruskal-Wallis 检验", ["H", "p"], [[_fmt(stat, 4), _fmt(p_val, 4)]]),
        _sec_advice("Kruskal-Wallis 检验适合三个及以上独立样本的非参数比较。"),
        _sec_smart(f"Kruskal-Wallis 检验完成，p 值为 {_fmt(p_val, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["组别", "N", "中位数"], "rows": desc_rows, "description": "Kruskal-Wallis 检验完成。", "sections": sections}
