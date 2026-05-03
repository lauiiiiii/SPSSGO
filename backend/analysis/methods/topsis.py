# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "topsis"
METHOD_META = {'label': '优劣解距离法(TOPSIS)',
 'category': '综合评价',
 'description': '基于与理想解和负理想解的距离进行综合排序',
 'order': 50,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "TOPSIS 至少需要 2 个指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    vector_norm = np.sqrt((data ** 2).sum(axis=0)).replace(0, np.nan)
    standardized = data.div(vector_norm, axis=1).fillna(0.0)
    weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    weighted = standardized.mul(weights, axis=1)
    ideal = weighted.max(axis=0)
    anti_ideal = weighted.min(axis=0)
    d_pos = np.sqrt(((weighted - ideal) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - anti_ideal) ** 2).sum(axis=1))
    closeness = d_neg / (d_pos + d_neg).replace(0, np.nan)
    closeness = closeness.fillna(0.0)

    rows = [[str(idx), _fmt(d_pos.loc[idx], 4), _fmt(d_neg.loc[idx], 4), _fmt(closeness.loc[idx], 4)] for idx in closeness.sort_values(ascending=False).head(10).index]
    weight_rows = [[var, _fmt(weights[var], 4), _fmt(ideal[var], 4), _fmt(anti_ideal[var], 4)] for var in variables]
    sections = [
        _sec_table("TOPSIS 指标概况", ["指标", "权重", "正理想解", "负理想解"], weight_rows),
        _sec_table("TOPSIS 排序 Top10", ["样本索引", "到正理想距离", "到负理想距离", "贴近度"], rows),
        _sec_advice("贴近度越接近 1，说明该样本越接近理想方案。当前版本默认等权重。"),
        _sec_smart(f"TOPSIS 分析完成，当前贴近度最高的样本索引为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["样本索引", "到正理想距离", "到负理想距离", "贴近度"], "rows": rows, "description": f"TOPSIS 分析完成，共排序 {len(closeness)} 个样本。", "sections": sections}
