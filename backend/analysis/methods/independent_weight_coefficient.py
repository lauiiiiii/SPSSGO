# -*- coding: utf-8 -*-
# 独立性权系数法入口：对齐 SPSSAU 输出颗粒度。
# 按 SPSSPRO 口径，用复相关系数R衡量指标间共线性，1/R 作为权系数，归一化得到权重(%)。
# 别和 CRITIC / 熵值法搞混，这里只看"能不能被其它指标线性解释"。
import math

from backend.analysis.common import *

METHOD_KEY = "independent_weight_coefficient"
METHOD_META = {
    "label": "独立性权系数法",
    "category": "综合评价",
    "description": "依据各指标与其他指标之间的复相关系数确定客观权重，复相关系数越大说明信息重复越多、权重越小",
    "order": 110,
    "slots": [
        {
            "key": "variables",
            "label": "评价指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入综合评价指标",
        }
    ],
    "options": [],
    "param_builder": "direct",
}

_REFS = _REFS_GENERAL + [
    "[3] 贾征, 高尔生, 魏建华. 综合评价中权重系数及标准化方法的研究[J]. 中国公共卫生, 2001, 17(11): 1048-1050.",
]


def _error(message):
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": message}


def _as_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


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


def _describe_rows(data, variables):
    rows = []
    for variable in variables:
        series = pd.to_numeric(data[variable], errors="coerce").dropna()
        rows.append([
            variable,
            str(len(series)),
            _fmt(series.mean(), 3),
            _fmt(series.std(ddof=1), 3) if len(series) > 1 else "0.000",
        ])
    return rows


def _weight_chart(rows):
    ordered = sorted(rows, key=lambda row: float(row[3]), reverse=True)
    return {
        "chartType": "metric_comparison",
        "title": "权重值",
        "data": {
            "metric": "权重(%)",
            "labels": [row[0] for row in ordered],
            "values": [float(row[3]) for row in ordered],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
            "axisLabels": {"x": "指标", "y": "权重(%)"},
        },
    }


def _analysis_steps():
    return (
        "1. 计算各指标间的相关系数矩阵。\n"
        "2. 逐个指标计算对其它所有指标的复相关系数 R。\n"
        "3. 以 1/R 作为权系数，对 1/R 归一化得到权重(%)。\n"
        "4. 复相关系数R值越大说明重复信息越多，权重则越小。"
    )


def _result_explanation(rows, valid_count):
    ordered = sorted(rows, key=lambda row: float(row[3]), reverse=True)
    top = ordered[0]
    bottom = ordered[-1]
    return (
        f"独立性权系数法对 {len(rows)} 个指标进行客观赋权，有效样本量 N={valid_count}。"
        f"结果显示，{top[0]} 的权重最高（{top[3]}%），说明该指标被其他指标线性解释的程度最低，"
        f"独立信息量相对最多；{bottom[0]} 的权重最低（{bottom[3]}%），说明其信息重复度相对较高。"
    )


def _advice():
    return (
        "第一：复相关系数R衡量的是某指标能被其余指标线性解释的程度，R越大说明信息重复越多；\n"
        "第二：该方法只考虑指标间的共线性/独立性，不考虑指标自身的离散程度；\n"
        "第三：如果需要同时考虑变异性+冲突性，可对比 CRITIC 权重法；如果只按离散程度赋权，可对比变异系数法。"
    )


def run(df, params):
    """
    执行独立性权系数法权重分析。

    @param df: 当前数据集，样本为行、指标为列
    @param params: variables
    @return: 对齐 SPSSAU 的独立性权系数法结果、图表和描述统计 sections
    """
    params = params or {}
    variables = _resolve_cols(df, _as_list(params.get("variables", [])))
    if len(variables) < 2:
        return _error("独立性权系数法至少需要 2 个指标。")
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3:
        return _error("有效样本不足，独立性权系数法至少需要 3 条完整样本。")

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

    top_weight = max(rows, key=lambda row: float(row[3]))
    bottom_weight = min(rows, key=lambda row: float(row[3]))

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["评价指标", "、".join(variables)],
            ],
            description="SPSSGO 采用 SPSSAU 独立性权系数法入口：放入定量指标后计算复相关系数R、倒数1/R和权重。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(len(data))],
                ["排除样本量", str(len(df) - len(data))],
            ],
            description="若某样本在任意评价指标上缺失，该样本不进入独立性权系数法计算。",
        ),
        _sec_advice(_analysis_steps(), title="分析步骤"),
        _sec_table(
            "输出结果1：权重计算结果",
            headers,
            rows,
            description="上表展示了独立性权系数法的权重计算结果：复相关系数R值越大说明重复信息越多，权重则越小；权重由复相关系数倒数1/R值归一化得到。",
        ),
        _sec_charts(
            "输出结果2：权重值",
            [_weight_chart(rows)],
            "图中按权重百分比展示各指标重要度，默认按权重由高到低排序。",
        ),
        _sec_table(
            "输出结果3：描述统计",
            ["项", "样本量", "平均值", "标准差"],
            _describe_rows(data, variables),
            description="描述统计展示进入独立性权系数法模型的有效样本量、平均值和样本标准差。",
        ),
        _sec_advice(_result_explanation(rows, len(data)), title="详细结论"),
        _sec_advice(_advice()),
        _sec_smart(
            f"独立性权系数法完成，有效样本量 N={len(data)}；权重最高的指标为 {top_weight[0]}（{top_weight[3]}%），"
            f"权重最低的指标为 {bottom_weight[0]}（{bottom_weight[3]}%）。"
        ),
        _sec_refs(_REFS),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"独立性权系数法完成，共计算 {len(variables)} 个指标权重，有效样本量 N={len(data)}。",
        "sections": sections,
    }
