# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "manova"
METHOD_META = {'label': '多变量方差分析',
 'category': '差异对比分析包',
 'description': '同时检验多个因变量在组间的总体差异',
 'order': 65,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入分组变量'},
           {'key': 'dependent_vars', 'label': '因变量', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入两个及以上因变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    try:
        from statsmodels.multivariate.manova import MANOVA
    except Exception as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"缺少 MANOVA 依赖：{str(exc)}"}
    group_var = params.get("group_var", "")
    dependent_vars = _resolve_cols(df, params.get("dependent_vars", []))
    needed = [group_var] + dependent_vars
    if group_var not in df.columns or len(dependent_vars) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量不存在，或因变量不足 2 个。"}
    temp = df[needed].copy()
    for dep in dependent_vars:
        temp[dep] = pd.to_numeric(temp[dep], errors="coerce")
    temp = temp.dropna()
    temp[group_var] = temp[group_var].astype("object")
    formula = " + ".join([f"Q('{dep}')" for dep in dependent_vars]) + f" ~ C(Q('{group_var}'))"
    model = MANOVA.from_formula(formula, data=temp)
    mv = model.mv_test()
    effect_key = next((key for key in mv.results if group_var in key), None)
    if effect_key is None:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "MANOVA 结果解析失败。"}
    stat_table = mv.results[effect_key]['stat']
    rows = [[idx, _fmt(row.get("Value"), 4), _fmt(row.get("F Value"), 4), _fmt(row.get("Pr > F"), 4)] for idx, row in stat_table.iterrows()]
    sections = [
        _sec_table("MANOVA 结果", ["统计量", "值", "F", "p"], rows),
        _sec_advice("多变量方差分析适合因变量不止一个且它们之间可能相关的情形。"),
        _sec_smart(f"多变量方差分析完成，共纳入 {len(temp)} 个有效样本。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["统计量", "值", "F", "p"], "rows": rows, "description": "多变量方差分析完成。", "sections": sections}
