# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "grey_relational_analysis"
METHOD_META = {'label': '灰色关联分析',
 'category': '综合评价',
 'description': '通过比较序列与参考序列的接近程度评估关联强弱',
 'order': 120,
 'slots': [{'key': 'reference_var', 'label': '参考序列', 'type': 'single', 'accept': 'numeric', 'hint': '放入参考变量'},
           {'key': 'compare_vars', 'label': '比较序列', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入比较变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    reference_var = params.get("reference_var", "")
    compare_vars = _resolve_cols(df, params.get("compare_vars", []))
    if reference_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "参考序列不存在。"}
    if not compare_vars:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 1 个比较序列。"}
    data = df[[reference_var] + compare_vars].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    normalized = _normalize_benefit_frame(data)
    ref = normalized[reference_var]
    delta = (normalized[compare_vars].sub(ref, axis=0)).abs()
    delta_min = float(delta.min().min())
    delta_max = float(delta.max().max())
    rho = 0.5
    coeff = (delta_min + rho * delta_max) / (delta + rho * delta_max + 1e-12)
    grade = coeff.mean(axis=0).sort_values(ascending=False)
    rows = [[var, _fmt(grade[var], 4)] for var in grade.index]
    sections = [
        _sec_table("灰色关联度结果", ["比较序列", "关联度"], rows),
        _sec_advice("灰色关联度越高，说明该指标与参考序列变化趋势越接近。"),
        _sec_smart(f"灰色关联分析完成，与 {reference_var} 关联度最高的变量为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["比较序列", "关联度"], "rows": rows, "description": f"灰色关联分析完成，共比较 {len(compare_vars)} 个序列。", "sections": sections}
