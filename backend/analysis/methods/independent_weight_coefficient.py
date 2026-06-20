# -*- coding: utf-8 -*-
# spssgo
# 独立性权系数法：按 SPSSPRO 口径，用复相关系数R衡量指标间共线性，
# 1/R 作为权系数，归一化得到权重(%)。
# 别和 CRITIC / 熵值法搞混，这里只看"能不能被其它指标线性解释"。
import math

from backend.analysis.common import *

METHOD_KEY = "independent_weight_coefficient"
METHOD_META = {'label': '独立性权系数法',
 'category': '综合评价',
 'description': '依据各指标与其他指标之间的复相关系数确定客观权重，复相关系数越大说明信息重复越多、权重越小',
 'order': 110,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}

_REFS = [
    "贾征, 高尔生, 魏建华. 综合评价中权重系数及标准化方法的研究[J]. 中国公共卫生, 2001, 17(11): 1048-1050.",
    "SPSSPRO. 独立性权系数法[EB/OL]. https://www.spsspro.com.",
]


def _multiple_correlation(corr_matrix, target_idx, other_indices):
    """计算 target 对其它所有指标的复相关系数 R。

    R² = r' * R_inv * r，其中 r 是 target 与其余指标的相关向量，
    R_inv 是其余指标相关矩阵的逆。R 取 sqrt 后保证非负。
    矩阵奇异时退化到 0，对应指标完全可由其它指标线性表示。
    """
    r = corr_matrix.loc[other_indices, target_idx].values
    R_sub = corr_matrix.loc[other_indices, other_indices].values
    try:
        R_inv = np.linalg.inv(R_sub)
        r_sq = float(r @ R_inv @ r)
    except np.linalg.LinAlgError:
        r_sq = 0.0
    r_sq = max(0.0, min(1.0, r_sq))
    return math.sqrt(r_sq)


def _weight_chart(rows):
    return {
        "chartType": "metric_comparison",
        "title": "指标重要度直方图",
        "data": {
            "metric": "权重(%)",
            "labels": [row[0] for row in rows],
            "values": [float(row[2]) for row in rows],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
            "axisLabels": {"x": "指标", "y": "权重(%)"},
        },
    }


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [],
                "description": "独立性权系数法至少需要 2 个指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [],
                "description": "有效样本不足。"}

    corr = data.corr().abs().fillna(0.0)

    # 逐个指标计算对其它所有指标的复相关系数 R
    all_indices = list(range(len(variables)))
    r_values = {}
    inv_r_values = {}
    for i, var in enumerate(variables):
        other = [variables[j] for j in all_indices if j != i]
        r = _multiple_correlation(corr, var, other)
        r_values[var] = r
        inv_r_values[var] = (1.0 / r) if r > 1e-10 else 1e10

    # 对 1/R 归一化得到权重
    inv_sum = sum(inv_r_values.values())
    weights = {var: inv_r_values[var] / inv_sum for var in variables}

    headers = ["项", "复相关系数R", "复相关系数倒数1/R", "权重(%)"]
    rows = [
        [var, _fmt(r_values[var], 3), _fmt(inv_r_values[var], 3), _fmt(weights[var] * 100, 3)]
        for var in variables
    ]

    top_var = max(weights, key=weights.get)
    bottom_var = min(weights, key=weights.get)
    top_weight = _fmt(weights[top_var] * 100, 3)
    bottom_weight = _fmt(weights[bottom_var] * 100, 3)

    description = (
        f"独立性权系数法对各变量的权重（重要性）进行计算："
        f"{top_var}的权重为{top_weight}%，"
        + "、".join(f"{var}的权重为{_fmt(weights[var]*100, 3)}%" for var in variables if var != top_var)
        + f"。其中指标权重最大值为{top_var}（{top_weight}%），最小值为{bottom_var}（{bottom_weight}%）。"
    )

    table_description = (
        f"上表展示了独立性权系数法的权重计算结果，根据结果对各个指标的权重进行分析。\n"
        f"• 复相关系数R值越大说明重复信息越多，权重则越小。\n"
        f"• 复相关系数1/R值越大，则说明权重应该越大。\n"
        f"• 权重由复相关系数倒数1/R值归一化得到。"
    )

    chart_description = "上图以直方图形式展示了指标的权重排序（降序）。"

    smart_text = (
        f"独立性权系数法的权重计算结果显示，{top_var}的权重为{top_weight}%，"
        f"{bottom_var}的权重为{bottom_weight}%，"
        f"其中指标权重最大值为{top_var}（{top_weight}%），最小值为{bottom_var}（{bottom_weight}%）。"
    )

    sections = [
        _sec_table("输出结果1：权重计算结果", headers, rows, description=table_description),
        _sec_charts("输出结果2：指标重要度直方图", [_weight_chart(rows)], chart_description),
        _sec_advice(
            "第一：复相关系数R衡量的是某指标能被其余指标线性解释的程度，R越大说明信息重复越多；\n"
            "第二：该方法只考虑指标间的共线性/独立性，不考虑指标自身的离散程度；\n"
            "第三：如果需要同时考虑变异性+冲突性，可对比 CRITIC 权重法；如果只按离散程度赋权，可对比变异系数法。"
        ),
        _sec_smart(smart_text),
        _sec_refs(_REFS),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": description,
        "sections": sections,
    }
