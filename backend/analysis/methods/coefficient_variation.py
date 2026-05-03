# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "coefficient_variation"
METHOD_META = {'label': '变异系数法',
 'category': '综合评价',
 'description': '使用变异系数衡量指标离散程度并进行客观赋权',
 'order': 80,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "变异系数法至少需要 2 个数值型指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    means = data.mean().replace(0, np.nan)
    stds = data.std(ddof=1)
    cv = (stds / means.abs()).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    weights = cv / cv.sum() if float(cv.sum()) > 0 else pd.Series([1 / len(variables)] * len(variables), index=variables)
    normalized = _normalize_benefit_frame(data)
    score = normalized.mul(weights, axis=1).sum(axis=1)

    rows = [[var, _fmt(means[var], 4), _fmt(stds[var], 4), _fmt(cv[var], 4), _fmt(weights[var], 4)] for var in variables]
    sections = [
        _sec_table("变异系数权重结果", ["指标", "均值", "标准差", "变异系数", "权重"], rows),
        _sec_table("综合得分 Top10", ["样本索引", "综合得分"], _score_top10_rows(score)),
        _sec_advice("变异系数越大，说明指标区分度越强，在客观赋权中通常权重越高。"),
        _sec_smart(f"变异系数法完成，权重最高的指标为 {weights.sort_values(ascending=False).index[0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["指标", "均值", "标准差", "变异系数", "权重"], "rows": rows, "description": f"变异系数法完成，共计算 {len(variables)} 个指标权重。", "sections": sections}
