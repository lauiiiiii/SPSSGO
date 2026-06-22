# -*- coding: utf-8 -*-
# 优序图法权重分析入口：对齐 SPSSAU 优序图权重输出颗粒度。
# 按指标平均值两两对比（大=1，小=0，等=0.5），行和得 TTL 指标得分，归一化得权重值。
from backend.analysis.common import *


def inject_metadata(metadata_map, params):
    """注入变量标题，让输出用题目名而非变量名显示。"""
    enriched = dict(params or {})
    variables = _as_list(enriched.get("variables", []))
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in variables
    }
    return enriched

METHOD_KEY = "ranking_method"
METHOD_META = {
    "label": "优序图法",
    "category": "综合评价",
    "description": "按指标平均值两两对比计算优序图权重，适用于专家打分或样本均值赋权场景",
    "order": 70,
    "aliases": ["优序图法", "优序图", "ranking_method"],
    "slots": [
        {
            "key": "variables",
            "label": "评价指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入需要计算优序图权重的定量指标",
        }
    ],
    "options": [],
    "param_builder": "direct",
}

_REFS_RANKING = _REFS_GENERAL + [
    "[3] 谭跃进. 定量分析方法[M]. 北京: 中国人民大学出版社, 2012.",
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


def _build_ranking_matrix(data, variables):
    """构建优序图权重计算表：平均值 + 两两对比矩阵（1/0/0.5）。"""
    means = data[variables].mean()
    n = len(variables)
    matrix = []
    for i, var_i in enumerate(variables):
        row = [var_i]
        for j, var_j in enumerate(variables):
            if i == j:
                row.append(0.5)
            else:
                diff = means[var_i] - means[var_j]
                if abs(diff) < 1e-12:
                    row.append(0.5)
                elif diff > 0:
                    row.append(1.0)
                else:
                    row.append(0.0)
        matrix.append(row)
    return means, matrix


def _ranking_matrix_rows(means, matrix, variables, display_labels=None):
    """优序图权重计算表的行数据。"""
    display_labels = display_labels or {}
    rows = []
    for i, var in enumerate(variables):
        row = [display_labels.get(var, var), _fmt(means[var], 3)]
        for val in matrix[i][1:]:
            row.append(_fmt(val, 1) if val != 0.5 else "0.5")
        rows.append(row)
    return rows


def _ttl_scores(matrix, variables):
    """计算每行 TTL（指标得分）。"""
    ttls = []
    for i in range(len(variables)):
        ttl = sum(matrix[i][1:])
        ttls.append(ttl)
    return ttls


def _weight_rows(variables, means, ttls, weights, display_labels=None):
    """优序图权重计算结果的行数据。"""
    display_labels = display_labels or {}
    rows = []
    for i, var in enumerate(variables):
        rows.append([
            display_labels.get(var, var),
            _fmt(means[var], 3),
            _fmt(ttls[i], 3),
            _fmt(weights[i] * 100, 3) + "%",
        ])
    return rows


def _weight_chart(rows):
    ordered = sorted(rows, key=lambda row: float(row[3].rstrip("%")), reverse=True)
    return {
        "chartType": "metric_comparison",
        "title": "权重值",
        "data": {
            "metric": "权重(%)",
            "labels": [row[0] for row in ordered],
            "values": [float(row[3].rstrip("%")) for row in ordered],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
            "axisLabels": {"x": "指标", "y": "权重(%)"},
        },
    }


def run(df, params):
    """
    执行优序图法权重分析。

    @param df: 当前数据集，样本为行、指标为列
    @param params: variables、variable_labels
    @return: 对齐 SPSSAU 的优序图权重结果、图表和描述统计 sections
    """
    params = params or {}
    variables = _resolve_cols(df, _as_list(params.get("variables", [])))
    if len(variables) < 2:
        return _error("优序图法至少需要 2 个数值型指标。")

    # 用题目名替代变量名显示
    variable_labels = params.get("variable_labels", {})
    display_labels = {v: variable_labels.get(v, v) for v in variables}

    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    data = numeric.loc[complete_mask, variables]
    if len(data) < 2:
        return _error("有效样本不足，优序图法至少需要 2 条完整样本。")

    means, matrix = _build_ranking_matrix(data, variables)
    matrix_headers = ["项"] + [display_labels[v] for v in variables]
    matrix_rows = _ranking_matrix_rows(means, matrix, variables, display_labels)

    ttls = _ttl_scores(matrix, variables)
    ttl_sum = sum(ttls)
    if ttl_sum > 0:
        weights = [ttl / ttl_sum for ttl in ttls]
    else:
        weights = [1.0 / len(variables)] * len(variables)

    result_headers = ["项", "平均值", "TTL(指标得分)", "权重值"]
    result_rows = _weight_rows(variables, means, ttls, weights, display_labels)

    # 对齐 SPSSAU 优序图法输出：只保留核心结果表 + 分析建议 + 权重图 + 参考文献
    sections = [
        _sec_table(
            "优序图权重计算表",
            matrix_headers,
            matrix_rows,
            description="优序图法计算权重时，首先需要构建优序图权重表（SPSSGO自动构建），正如上表格所示；\n"
                        "第一：优序图权重表构建方式为：计算出各分析项的平均值，接着利用平均值大小进行两两对比；\n"
                        "第二：平均值相对更大时计为1分，相对更小时计为0分，平均值完全相等时计为0.5分；\n"
                        "第三：平均值越大意味着重要性越高（请确保是此类数据），权重也会越高。",
        ),
        _sec_table(
            "优序图权重计算结果表",
            result_headers,
            result_rows,
            description="完成优序图权重计算表后，接着计算TTL值最终得到权重值；\n"
                        "第一：结合优序图权重计算表，针对每行数据求和，得到TTL值；\n"
                        "第二：针对TTL值进行归一化处理，最终得到权重值。",
        ),
        _sec_advice(
            "完成优序图权重计算表后，接着计算TTL值最终得到权重值；\n"
            "第一：结合优序图权重计算表，针对每行数据求和，得到TTL值；\n"
            "第二：针对TTL值进行归一化处理，最终得到权重值。",
            title="分析建议",
        ),
        _sec_charts(
            "权重值",
            [_weight_chart(result_rows)],
        ),
        _sec_refs(_REFS_RANKING),
    ]

    return {
        "name": METHOD_META["label"],
        "headers": result_headers,
        "rows": result_rows,
        "description": f"优序图法完成，共计算 {len(variables)} 个指标权重，有效样本量 N={valid_count}。",
        "sections": sections,
    }
