# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "one_sample_equivalence_test"
METHOD_META = {'label': '单样本等价性检验',
 'category': '差异对比分析包',
 'description': '使用 TOST 检验单样本均值是否落在等价区间内',
 'order': 70,
 'slots': [{'key': 'variable', 'label': '检验变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入检验变量'}],
 'options': [{'key': 'reference_value', 'label': '参考值', 'choices': ['0', '1', '5'], 'default': '0'},
             {'key': 'margin', 'label': '等价界值', 'choices': ['0.5', '1', '2'], 'default': '1'}],
 'param_builder': 'direct'}


def run(df, params):
    variable = params.get("variable", "")
    if variable not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "检验变量不存在。"}
    ref = float(params.get("reference_value", 0) or 0)
    margin = abs(float(params.get("margin", 1) or 1))
    series = pd.to_numeric(df[variable], errors="coerce").dropna()
    if len(series) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    mean = float(series.mean())
    se = float(series.std(ddof=1) / np.sqrt(len(series)))
    dfree = len(series) - 1
    t1 = (mean - (ref - margin)) / se
    p1 = 1 - stats.t.cdf(t1, dfree)
    t2 = ((ref + margin) - mean) / se
    p2 = 1 - stats.t.cdf(t2, dfree)
    passed = max(p1, p2) < 0.05
    rows = [["下界检验", _fmt(t1, 4), _fmt(p1, 4)], ["上界检验", _fmt(t2, 4), _fmt(p2, 4)], ["是否等价", "是" if passed else "否", ""]]
    sections = [
        _sec_table("单样本等价性检验（TOST）", ["检验", "t", "p"], rows),
        _sec_advice("TOST 要求上下界检验都显著，才能认为样本均值与参考值等价。"),
        _sec_smart(f"单样本等价性检验完成，结果为{'通过' if passed else '未通过'}等价性。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["检验", "t", "p"], "rows": rows, "description": "单样本等价性检验完成。", "sections": sections}
