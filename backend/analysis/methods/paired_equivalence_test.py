# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "paired_equivalence_test"
METHOD_META = {'label': '配对样本等价性检验',
 'category': '差异对比分析包',
 'description': '使用 TOST 检验配对样本差值是否落在等价区间内',
 'order': 80,
 'slots': [{'key': 'var1', 'label': '变量1', 'type': 'single', 'accept': 'numeric', 'hint': '放入第一个配对变量'},
           {'key': 'var2', 'label': '变量2', 'type': 'single', 'accept': 'numeric', 'hint': '放入第二个配对变量'}],
 'options': [{'key': 'margin', 'label': '等价界值', 'choices': ['0.5', '1', '2'], 'default': '1'}],
 'param_builder': 'direct'}


def run(df, params):
    var1 = params.get("var1", "")
    var2 = params.get("var2", "")
    margin = abs(float(params.get("margin", 1) or 1))
    if var1 not in df.columns or var2 not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "配对变量不存在。"}
    temp = df[[var1, var2]].apply(pd.to_numeric, errors="coerce").dropna()
    diff = temp[var1] - temp[var2]
    if len(diff) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    mean_diff = float(diff.mean())
    se = float(diff.std(ddof=1) / np.sqrt(len(diff)))
    dfree = len(diff) - 1
    t1 = (mean_diff + margin) / se
    p1 = 1 - stats.t.cdf(t1, dfree)
    t2 = (margin - mean_diff) / se
    p2 = 1 - stats.t.cdf(t2, dfree)
    passed = max(p1, p2) < 0.05
    rows = [["下界检验", _fmt(t1, 4), _fmt(p1, 4)], ["上界检验", _fmt(t2, 4), _fmt(p2, 4)], ["是否等价", "是" if passed else "否", ""]]
    sections = [
        _sec_table("配对样本等价性检验（TOST）", ["检验", "t", "p"], rows),
        _sec_advice("配对样本等价性检验适合前后测、一致性验证或替代方法比较场景。"),
        _sec_smart(f"配对样本等价性检验完成，结果为{'通过' if passed else '未通过'}等价性。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["检验", "t", "p"], "rows": rows, "description": "配对样本等价性检验完成。", "sections": sections}
