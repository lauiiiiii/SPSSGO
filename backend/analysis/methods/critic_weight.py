# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "critic_weight"
METHOD_META = {'label': 'CRITIC权重法',
 'category': '综合评价',
 'description': '综合考虑指标对比强度与冲突性进行客观赋权',
 'order': 100,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "CRITIC 权重法至少需要 2 个指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    normalized = _normalize_benefit_frame(data)
    stds = normalized.std(ddof=1)
    corr = normalized.corr().fillna(0.0)
    conflict = (1 - corr).sum(axis=0)
    critic = stds * conflict
    weights = critic / critic.sum() if float(critic.sum()) > 0 else pd.Series([1 / len(variables)] * len(variables), index=variables)
    score = normalized.mul(weights, axis=1).sum(axis=1)

    rows = [[var, _fmt(stds[var], 4), _fmt(conflict[var], 4), _fmt(critic[var], 4), _fmt(weights[var], 4)] for var in variables]
    sections = [
        _sec_table("CRITIC 权重结果", ["指标", "标准差", "冲突性", "信息量", "权重"], rows),
        _sec_table("综合得分 Top10", ["样本索引", "综合得分"], _score_top10_rows(score)),
        _sec_advice("CRITIC 权重法会同时考虑指标离散程度和指标之间的信息重复程度。"),
        _sec_smart(f"CRITIC 权重法完成，信息量最高的指标为 {critic.sort_values(ascending=False).index[0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["指标", "标准差", "冲突性", "信息量", "权重"], "rows": rows, "description": f"CRITIC 权重法完成，共计算 {len(variables)} 个指标权重。", "sections": sections}
