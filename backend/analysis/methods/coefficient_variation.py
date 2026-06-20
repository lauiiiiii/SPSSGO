# -*- coding: utf-8 -*-
# 变异系数法入口：对齐 SPSSPRO“变异系数法”和 SPSSAU“信息量权重”的共同权重口径。
# 这里只做指标客观赋权，综合得分回写后续单独接，别把排序表硬塞进权重报告。
from backend.analysis.common import *

METHOD_KEY = "coefficient_variation"
METHOD_META = {
    "label": "变异系数法（信息量权重）",
    "navLabel": "变异系数法",
    "category": "综合评价",
    "description": "使用变异系数衡量指标离散程度并进行客观赋权，兼容 SPSSAU 信息量权重口径",
    "order": 80,
    "aliases": ["变异系数法", "信息量权重", "信息量权重法", "CV权重法"],
    "slots": [
        {
            "key": "variables",
            "label": "评价指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入需要计算信息量权重的定量指标",
        }
    ],
    "options": [],
    "param_builder": "direct",
}

_REFS_CV = _REFS_GENERAL + [
    "[3] 刘盼盼,任广跃,段续,李琳,赵路洁,任星,曲峥伟. 基于变异系数法对不同干燥方式白萝卜品质及风味的评价[J/OL]. 食品与发酵工业:1-11.",
]


def _error(message):
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": message}


def _weight_rows(variables, means, stds, cv, weights):
    return [
        [
            variable,
            _fmt(means[variable], 3),
            _fmt(stds[variable], 3),
            _fmt(cv[variable], 3),
            _fmt(weights[variable] * 100, 3),
        ]
        for variable in variables
    ]


def _weight_chart(rows):
    return {
        "chartType": "metric_comparison",
        "title": "指标重要度直方图",
        "data": {
            "metric": "权重(%)",
            "labels": [row[0] for row in rows],
            "values": [float(row[4]) for row in rows],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
            "axisLabels": {"x": "指标", "y": "权重(%)"},
        },
    }


def _weight_description(rows, valid_count):
    top = max(rows, key=lambda row: float(row[4]))
    bottom = min(rows, key=lambda row: float(row[4]))
    return (
        f"上表展示变异系数法的权重计算结果，有效样本量 N={valid_count}。"
        f"结果显示，{top[0]} 的权重最高（{top[4]}%），说明该指标在样本中的相对离散程度最大，"
        f"提供的信息量相对更多；{bottom[0]} 的权重最低（{bottom[4]}%），说明其相对离散程度较小。"
    )


def _chart_description(rows):
    ordered = sorted(rows, key=lambda row: float(row[4]), reverse=True)
    return (
        "图中按权重大小展示各指标的重要度。"
        f"权重排序前三的指标为{', '.join(row[0] for row in ordered[:3])}，解释时应结合指标业务含义判断其实际重要性。"
    )


def _academic_interpretation(rows, valid_count):
    top = max(rows, key=lambda row: float(row[4]))
    return (
        f"本次采用变异系数法（信息量权重）对 {len(rows)} 个指标进行客观赋权，有效样本量为 N={valid_count}。"
        "该方法先计算各指标的均值和样本标准差，再以标准差与均值之比作为变异系数，"
        "最后对各指标变异系数进行归一化得到权重。"
        f"结果显示，{top[0]} 的权重最高（{top[4]}%），表明其在当前样本中差异程度最大，"
        "对综合评价结果的区分作用相对更强。需要注意，变异系数法属于客观赋权方法，"
        "权重反映的是样本数据的离散程度，不等同于理论或业务上的主观重要性。"
    )


def _advice():
    return (
        "第一：变异系数法要求指标均值为正，均值接近 0 时权重会不稳定；\n"
        "第二：该方法只根据指标相对离散程度赋权，不考虑指标之间的相关性；\n"
        "第三：如果需要同时考虑指标冲突性，可对比 CRITIC 权重法；如果需要熵信息口径，可对比熵权法。"
    )


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return _error("变异系数法（信息量权重）至少需要 2 个数值型指标。")
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return _error("有效样本不足，变异系数法至少需要 2 条完整样本。")

    means = data.mean()
    invalid_means = [variable for variable in variables if means[variable] <= 0]
    if invalid_means:
        return _error(f"变异系数法要求各指标均值大于 0，以下指标不满足：{', '.join(invalid_means)}。")
    stds = data.std(ddof=1)
    cv = (stds / means).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    cv_sum = float(cv.sum())
    if cv_sum > 0:
        weights = cv / cv_sum
    else:
        weights = pd.Series([1 / len(variables)] * len(variables), index=variables)

    headers = ["项", "平均值", "标准差", "CV系数", "权重(%)"]
    rows = _weight_rows(variables, means, stds, cv, weights)
    sections = [
        _sec_table(
            "输出结果1：权重计算结果",
            headers,
            rows,
            description=_weight_description(rows, len(data)),
        ),
        _sec_charts(
            "输出结果2：指标重要度直方图",
            [_weight_chart(rows)],
            _chart_description(rows),
        ),
        _sec_advice(
            "1. 计算各指标的平均值和样本标准差。\n"
            "2. 按 V_i=σ_i/X_i 计算各指标变异系数，变异系数越大表示样本差异越大。\n"
            "3. 按 W_i=V_i/ΣV_i 对变异系数进行归一化，得到各指标权重。",
            title="分析步骤",
        ),
        _sec_advice(_academic_interpretation(rows, len(data)), title="结果解释"),
        _sec_advice(_advice()),
        _sec_smart(
            f"变异系数法（信息量权重）完成，权重最高的指标为 "
            f"{max(rows, key=lambda row: float(row[4]))[0]}。"
        ),
        _sec_refs(_REFS_CV),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"变异系数法（信息量权重）完成，共计算 {len(variables)} 个指标权重。",
        "sections": sections,
    }
