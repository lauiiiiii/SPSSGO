# -*- coding: utf-8 -*-
# CRITIC 权重法入口：对齐 SPSSPRO/SPSSAU 的权重表、权重图和描述统计颗粒度。
# 这里只做客观赋权；综合得分只在用户显式勾选保存时回写，别默认塞排序表。
from backend.analysis.common import *

METHOD_KEY = "critic_weight"
METHOD_META = {
    "label": "CRITIC权重法",
    "category": "综合评价",
    "description": "综合考虑指标对比强度与冲突性进行客观赋权",
    "order": 100,
    "aliases": ["CRITIC权重", "CRITIC权重法", "critic"],
    "slots": [
        {
            "key": "variables",
            "label": "评价指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入需要计算 CRITIC 权重的定量指标",
        }
    ],
    "options": [
        {
            "key": "save_composite_score",
            "label": "保存综合得分",
            "type": "checkbox",
            "default": False,
            "hint": "选中后生成新数据版本，按 CRITIC 权重保存综合得分；未设置方向时默认各指标越大越好。",
        }
    ],
    "param_builder": "direct",
}

_REFS_CRITIC = _REFS_GENERAL + [
    "[3] Diakoulaki D, Mavrotas G, Papayannakis L. Determining objective weights in multiple criteria problems: The CRITIC method[J]. Computers & Operations Research, 1995, 22(7): 763-770.",
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


def _as_bool(value, default=False):
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "是", "勾选"}


def _critic_components(data, variables):
    stds = data[variables].std(ddof=1).fillna(0.0)
    corr = data[variables].corr()
    for variable in variables:
        corr.loc[variable, variable] = 1.0
    corr = corr.fillna(0.0)
    conflict = (1 - corr).sum(axis=0).clip(lower=0)
    information = stds * conflict
    total_information = float(information.sum())
    if total_information > 0:
        weights = information / total_information
    else:
        weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    return stds, conflict, information, weights


def _weight_rows(variables, stds, conflict, information, weights):
    return [
        [
            variable,
            _fmt(stds[variable], 3),
            _fmt(conflict[variable], 3),
            _fmt(information[variable], 3),
            _fmt(weights[variable] * 100, 3),
        ]
        for variable in variables
    ]


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
    ordered = sorted(rows, key=lambda row: float(row[4]), reverse=True)
    return {
        "chartType": "metric_comparison",
        "title": "权重值",
        "data": {
            "metric": "权重(%)",
            "labels": [row[0] for row in ordered],
            "values": [float(row[4]) for row in ordered],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
                {"value": "line", "label": "折线图"},
            ],
            "axisLabels": {"x": "指标", "y": "权重(%)"},
        },
    }


def _score_columns(df, score):
    row_positions = {row_index: position for position, row_index in enumerate(df.index)}
    values = [None] * len(df)
    for row_index, value in score.items():
        position = row_positions.get(row_index)
        if position is None:
            continue
        values[position] = None if pd.isna(value) else round(float(value), 6)
    return [{"base_name": "CompScore_CRITIC权重法", "values": values}]


def _analysis_steps():
    return (
        "1. 剔除任一评价指标缺失的样本，得到有效样本。\n"
        "2. 计算各指标的样本标准差，作为指标变异性；标准差越大，指标差异越大。\n"
        "3. 计算指标间相关矩阵，并按 Σ(1-rjk) 得到指标冲突性；相关性越强，冲突性越低。\n"
        "4. 以指标变异性乘以指标冲突性得到信息量，再对信息量归一化得到权重。"
    )


def _result_explanation(rows, valid_count):
    ordered = sorted(rows, key=lambda row: float(row[4]), reverse=True)
    top = ordered[0]
    bottom = ordered[-1]
    return (
        f"CRITIC权重法对 {len(rows)} 个指标进行客观赋权，有效样本量 N={valid_count}。"
        f"结果显示，{top[0]} 的权重最高（{top[4]}%），说明该指标同时具备较强的样本变异性和信息冲突性；"
        f"{bottom[0]} 的权重最低（{bottom[4]}%），说明其在当前数据中提供的独立信息量相对较少。"
    )


def _advice():
    return (
        "第一：CRITIC权重反映的是当前样本中的客观信息量，不等同于专家主观重要性；\n"
        "第二：如果指标量纲差异极大，需先确认是否应该在数据处理阶段做统一量纲处理；\n"
        "第三：若只希望依据离散程度赋权，可对比变异系数法；若希望按信息熵口径赋权，可对比熵值法。"
    )


def run(df, params):
    """
    执行 CRITIC 权重法。

    @param df: 当前数据集，样本为行、指标为列
    @param params: variables、save_composite_score
    @return: 对齐 SPSSPRO/SPSSAU 的 CRITIC 权重结果、图表和描述统计 sections
    """
    params = params or {}
    variables = _resolve_cols(df, _as_list(params.get("variables", [])))
    if len(variables) < 2:
        return _error("CRITIC 权重法至少需要 2 个数值型指标。")

    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    data = numeric.loc[complete_mask, variables]
    if len(data) < 3:
        return _error("有效样本不足，CRITIC 权重法至少需要 3 条完整样本。")

    stds, conflict, information, weights = _critic_components(data, variables)
    rows = _weight_rows(variables, stds, conflict, information, weights)
    headers = ["项", "指标变异性", "指标冲突性", "信息量", "权重(%)"]
    top_weight = max(rows, key=lambda row: float(row[4]))
    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["评价指标", "、".join(variables)],
                ["保存综合得分", "开启" if _as_bool(params.get("save_composite_score"), default=False) else "关闭"],
                ["变异性口径", "样本标准差"],
            ],
            description="SPSSGO 采用 SPSSPRO/SPSSAU 共同的 CRITIC 入口：放入定量指标后计算指标变异性、冲突性、信息量和权重。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意评价指标上缺失，该样本不进入 CRITIC 权重计算。",
        ),
        _sec_advice(_analysis_steps(), title="分析步骤"),
        _sec_table(
            "输出结果1：权重计算结果",
            headers,
            rows,
            description="上表展示 CRITIC 法权重计算结果：指标变异性为样本标准差，指标冲突性由相关系数矩阵计算得到，权重为信息量归一化结果。",
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
            description="描述统计展示进入 CRITIC 模型的有效样本量、平均值和样本标准差。",
        ),
        _sec_advice(_result_explanation(rows, valid_count), title="详细结论"),
        _sec_advice(_advice()),
        _sec_smart(
            f"CRITIC 权重法完成，有效样本量 N={valid_count}；权重最高的指标为 {top_weight[0]}（{top_weight[4]}%）。"
        ),
        _sec_refs(_REFS_CRITIC),
    ]

    result = {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"CRITIC 权重法完成，共计算 {len(variables)} 个指标权重，有效样本量 N={valid_count}。",
        "sections": sections,
    }
    if _as_bool(params.get("save_composite_score"), default=False):
        normalized = _normalize_benefit_frame(data)
        score = normalized.mul(weights, axis=1).sum(axis=1)
        result["score_columns"] = _score_columns(df, score)
    return result
