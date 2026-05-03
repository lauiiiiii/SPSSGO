# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "entropy_weight"
METHOD_META = {'label': '权重分析(熵权法)',
 'category': '高级问卷分析包',
 'description': '依据指标离散程度自动分配客观权重',
 'order': 160,
 'slots': [{'key': 'variables',
            'label': '指标变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}
def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "熵权法至少需要 2 个数值型指标。"}

    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    normalized = data.copy()
    for variable in variables:
        series = normalized[variable]
        range_value = series.max() - series.min()
        if range_value == 0:
            normalized[variable] = 1.0
        else:
            normalized[variable] = (series - series.min()) / range_value + 1e-12

    proportion = normalized.div(normalized.sum(axis=0), axis=1).replace(0, 1e-12)
    sample_count = len(proportion)
    k = 1.0 / np.log(sample_count)
    entropy = -k * (proportion * np.log(proportion)).sum(axis=0)
    divergence = 1 - entropy
    if float(divergence.sum()) == 0:
        weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    else:
        weights = divergence / divergence.sum()
    score = normalized.mul(weights, axis=1).sum(axis=1)

    headers = ["指标", "熵值", "差异系数", "权重"]
    rows = [
        [variable, _fmt(entropy[variable], 4), _fmt(divergence[variable], 4), _fmt(weights[variable], 4)]
        for variable in variables
    ]
    top_scores = score.sort_values(ascending=False).head(10)
    score_rows = [[str(index), _fmt(value, 4)] for index, value in top_scores.items()]

    sections = [
        _sec_table("熵权结果", headers, rows, description="熵值越低、差异系数越高，通常意味着该指标提供的信息量越大，权重也越高。"),
        _sec_table(
            "综合得分概况",
            ["指标", "值"],
            [
                ["有效样本量", str(len(data))],
                ["综合得分均值", _fmt(score.mean(), 4)],
                ["综合得分最小值", _fmt(score.min(), 4)],
                ["综合得分最大值", _fmt(score.max(), 4)],
            ],
        ),
        _sec_table("综合得分 Top10", ["样本索引", "综合得分"], score_rows),
        _sec_advice(
            "第一：当前实现按正向指标进行标准化，若存在逆向指标请先在数据处理环节完成方向统一；\n"
            "第二：熵权法更适合客观赋权场景，若研究需要主观权重，可结合 AHP 等方法联合使用。"
        ),
        _sec_smart(
            f"本次共纳入 {len(variables)} 个指标进行熵权分析，权重最高的指标为 "
            f"{weights.sort_values(ascending=False).index[0]}（权重 {_fmt(weights.max(), 4)}）。"
        ),
        _sec_refs(_REFS_GENERAL),
    ]

    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"熵权分析完成，共计算 {len(variables)} 个指标的客观权重。",
        "sections": sections,
    }
