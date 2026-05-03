# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "independent_weight_coefficient"
METHOD_META = {'label': '独立性权系数法',
 'category': '综合评价',
 'description': '依据指标独立性和离散程度构造综合客观权重',
 'order': 110,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "独立性权系数法至少需要 2 个指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    normalized = _normalize_benefit_frame(data)
    corr = normalized.corr().abs().fillna(0.0)
    independence = 1 - (corr.sum(axis=0) - 1) / max(len(variables) - 1, 1)
    variability = normalized.std(ddof=1)
    score_coef = independence * variability
    weights = score_coef / score_coef.sum() if float(score_coef.sum()) > 0 else pd.Series([1 / len(variables)] * len(variables), index=variables)
    score = normalized.mul(weights, axis=1).sum(axis=1)

    rows = [[var, _fmt(independence[var], 4), _fmt(variability[var], 4), _fmt(score_coef[var], 4), _fmt(weights[var], 4)] for var in variables]
    sections = [
        _sec_table("独立性权系数结果", ["指标", "独立性", "离散度", "权系数", "权重"], rows),
        _sec_table("综合得分 Top10", ["样本索引", "综合得分"], _score_top10_rows(score)),
        _sec_advice("该方法强调指标间低相关、低重复的信息价值，适合辅助客观赋权。"),
        _sec_smart(f"独立性权系数法完成，权重最高的指标为 {weights.sort_values(ascending=False).index[0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["指标", "独立性", "离散度", "权系数", "权重"], "rows": rows, "description": f"独立性权系数法完成，共计算 {len(variables)} 个指标权重。", "sections": sections}
