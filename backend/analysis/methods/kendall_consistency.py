# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "kendall_consistency"
METHOD_META = {'label': 'Kendall一致性检验',
 'category': '数据检验',
 'description': '评估多个评价对象排序结果之间的一致性程度',
 'order': 70,
 'slots': [{'key': 'variables', 'label': '评价变量', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入多个评价者或多轮排序结果'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个评价变量。"}
    temp = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(temp) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    ranked = temp.rank(axis=0, method="average")
    n, m = ranked.shape
    row_sums = ranked.sum(axis=1)
    s = ((row_sums - row_sums.mean()) ** 2).sum()
    w = 12 * s / (m ** 2 * (n ** 3 - n))
    chi2_val = m * (n - 1) * w
    p_val = 1 - stats.chi2.cdf(chi2_val, n - 1)
    rows = [["Kendall's W", _fmt(w, 4)], ["χ²", _fmt(chi2_val, 4)], ["df", str(n - 1)], ["p", _fmt(p_val, 4)]]
    sections = [
        _sec_table("Kendall 一致性结果", ["指标", "值"], rows),
        _sec_advice("Kendall's W 越接近 1，说明多个评价结果之间的一致性越高。"),
        _sec_smart(f"Kendall 一致性检验完成，W={_fmt(w, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["指标", "值"], "rows": rows, "description": "Kendall 一致性检验完成。", "sections": sections}
