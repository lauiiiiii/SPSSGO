# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "two_sample_equivalence_test"
METHOD_META = {'label': '双样本等价性检验',
 'category': '差异对比分析包',
 'description': '使用 TOST 检验两个独立样本均值差是否落在等价区间内',
 'order': 75,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入二分类分组变量'},
           {'key': 'test_var', 'label': '检验变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入检验变量'}],
 'options': [{'key': 'margin', 'label': '等价界值', 'choices': ['0.5', '1', '2'], 'default': '1'}],
 'param_builder': 'direct'}


def run(df, params):
    group_var = params.get("group_var", "")
    test_var = params.get("test_var", "")
    margin = abs(float(params.get("margin", 1) or 1))
    if group_var not in df.columns or test_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量或检验变量不存在。"}
    temp = df[[group_var, test_var]].copy()
    temp[test_var] = pd.to_numeric(temp[test_var], errors="coerce")
    temp = temp.dropna()
    groups = list(pd.Series(temp[group_var]).dropna().unique())
    if len(groups) != 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "双样本等价性检验需要恰好 2 个组。"}
    g1 = temp.loc[temp[group_var] == groups[0], test_var]
    g2 = temp.loc[temp[group_var] == groups[1], test_var]
    mean_diff = float(g1.mean() - g2.mean())
    se = float(np.sqrt(g1.var(ddof=1) / len(g1) + g2.var(ddof=1) / len(g2)))
    dfree = len(g1) + len(g2) - 2
    t1 = (mean_diff + margin) / se
    p1 = 1 - stats.t.cdf(t1, dfree)
    t2 = (margin - mean_diff) / se
    p2 = 1 - stats.t.cdf(t2, dfree)
    passed = max(p1, p2) < 0.05
    rows = [["下界检验", _fmt(t1, 4), _fmt(p1, 4)], ["上界检验", _fmt(t2, 4), _fmt(p2, 4)], ["是否等价", "是" if passed else "否", ""]]
    sections = [
        _sec_table("双样本等价性检验（TOST）", ["检验", "t", "p"], rows),
        _sec_advice("双样本等价性检验常用于药效、生物等效性或方法一致性场景。"),
        _sec_smart(f"双样本等价性检验完成，结果为{'通过' if passed else '未通过'}等价性。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["检验", "t", "p"], "rows": rows, "description": "双样本等价性检验完成。", "sections": sections}
