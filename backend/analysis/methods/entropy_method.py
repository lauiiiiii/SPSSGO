# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "entropy_method"
METHOD_META = {'label': '熵值法',
 'category': '综合评价',
 'description': '依据指标离散程度自动分配客观权重并计算综合得分',
 'order': 90,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "熵值法至少需要 2 个数值型指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    normalized = _normalize_benefit_frame(data)
    proportion = normalized.div(normalized.sum(axis=0), axis=1).replace(0, 1e-12)
    k = 1.0 / np.log(len(proportion))
    entropy = -k * (proportion * np.log(proportion)).sum(axis=0)
    divergence = 1 - entropy
    weights = divergence / divergence.sum() if float(divergence.sum()) > 0 else pd.Series([1 / len(variables)] * len(variables), index=variables)
    score = normalized.mul(weights, axis=1).sum(axis=1)

    rows = [[var, _fmt(entropy[var], 4), _fmt(divergence[var], 4), _fmt(weights[var], 4)] for var in variables]
    sections = [
        _sec_table("熵值法权重结果", ["指标", "熵值", "差异系数", "权重"], rows),
        _sec_table("综合得分概况", ["指标", "值"], [["有效样本量", str(len(data))], ["平均得分", _fmt(score.mean(), 4)], ["最大得分", _fmt(score.max(), 4)], ["最小得分", _fmt(score.min(), 4)]]),
        _sec_table("综合得分 Top10", ["样本索引", "综合得分"], _score_top10_rows(score)),
        _sec_advice("熵值法适合客观赋权场景。若包含逆向指标，请先统一方向。"),
        _sec_smart(f"熵值法计算完成，权重最高的指标为 {weights.sort_values(ascending=False).index[0]}（{_fmt(weights.max(), 4)}）。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["指标", "熵值", "差异系数", "权重"], "rows": rows, "description": f"熵值法完成，共计算 {len(variables)} 个指标的客观权重。", "sections": sections}
